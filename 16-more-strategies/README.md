# Chapter 16 — More Strategies: Momentum, Breakout, Event-driven

Ch7 §3-§5 catalogued **four families** of intraday strategies — mean-reversion (MR), momentum, breakout, and event-driven — and named the mechanism each one bets on. Ch8–Ch13 then took the *first* of those four (MR) on a full round-trip: raw signal (Ch7 §6) → walk-forward backtest (Ch11) → cost stack (Ch12) → execution rescue attempt (Ch13). The verdict on the QQQ closing-window MR strategy was Ch13's: **after-cost Sharpe −2.97**, and the passive-limit rescue failed to adverse selection. One family, deflated honestly through a five-step pipeline. Three families still on the shelf.

This chapter takes the other three off the shelf and runs them through the *same* pipeline. The intent is **fairness, not promotion**: every family gets the same backtest scaffolding, the same Ch12 cost stack, the same Ch13 execution treatment, and the same Ch15 regime conditioning. The pipeline is the instrument; the verdicts are what falls out of it. Most families are *expected* to fail. The interesting question is not "does anything beat MR?" but "if anything survives, does it survive the **same deflation arc** that killed MR?"

> **Definition — strategy family.** A class of intraday signals that share an entry *mechanism* — the economic or microstructural reason the signal is supposed to predict future returns. Ch7 §3-§5 named four: MR (fade the most recent move), momentum (continue the most recent move), breakout (act when price escapes a reference range), event-driven (trade around scheduled releases). Two strategies in the same family share their pain points: MR's pain is the bid-ask bounce eating its edge, breakout's pain is the false break, momentum's pain is trend reversion at the worst possible moment, event-driven's pain is sample size.

> **Foot-gun — surviving on the same data you searched.** Every result in this chapter was estimated on the same 251-session QQQ window that Ch7-Ch13 used. Anything that "wins" here was *selected* from a finite set of parameter cells on that single window. Ch10 §4's snooping discount applies to every survivor by construction. §5.3 makes the Bonferroni accounting explicit on the one cell that lands positive.

## Three things this chapter covers

1. **The other three families, run through the Ch9-Ch13 pipeline.** §2 momentum, §3 breakout, §4 event-driven. Same backtest scaffolding, same cost stack, same execution treatment. Three honest deflation passes side-by-side.
2. **Family-dependent execution.** §2.4, §3.5. Momentum *takes* liquidity by construction; breakout splits into a take-the-liquidity *confirmation* variant and a make-the-liquidity *anticipation* variant. The Ch13 toxicity diagnostic applies to anticipation and kills it.
3. **One survivor, deflated honestly.** §5.3. Among 9 sweep cells in §3.4, exactly one — ORB-confirm × OR-p75 × ε=10 — lands cost-aware Sharpe **+1.41 on 59 trades**. Bonferroni across the 3 × 3 grid drops the *operational* Sharpe estimate to **≈ +0.47**, and even that has a wide CI on N = 59. Ch17-18 paper-trades it, primarily as discipline.

## §1 — Setup

The chapter operates on **QQQ 1-min RTH bars** loaded from `06-bridge-to-intraday/data/qqq_1min.parquet` — the same source Ch6-Ch15 used. The window is ~2025-05-08 → 2026-05-07, 251 RTH sessions, ~95k minute bars.

### Ch7's four families restated, with this chapter's mechanism mapping

| Family | Mechanism (Ch7 §3-§5) | What this chapter does with it |
|---|---|---|
| Mean-reversion | Fade the most recent move; bet on Ch7 §6's negative lag-1 ρ. | Already deflated by Ch8-Ch13. Carried into §5.1 as the reference row. |
| **Momentum** | Continue the most recent move; bet on positive ρ at *longer* lags (Ch7 §6 hint: ρ ≈ +0.0043 at lag 120). | §2 — built, deflated, regime-conditioned. |
| **Breakout** | Act when price escapes a reference range, on the assumption that the escape is itself information. | §3 — built in two execution variants (confirmation, anticipation), deflated, regime-conditioned. |
| **Event-driven** | Trade around scheduled releases (FOMC, CPI, NFP); bet on pre-release drift or post-release continuation. | §4 — built on FOMC only; N = 8 sessions makes everything a wide-CI demonstration of *method*, not a verdict. |

### The five-step pipeline, restated

Every family in this chapter passes through the same five checkpoints, in order:

1. **Signal.** Define the predictor — a function of past bars that emits an entry rule.
2. **Backtest.** Event-driven single-position loop from Ch9 §2 with the Ch9 §3 ledger and the Ch9 §4 √(trades-per-year) annualizer.
3. **Cost-aware k\*.** Sweep the signal-threshold parameter; subtract the Ch12 cost stack per trade; report `argmax` of *post-cost* Sharpe (not pre-cost).
4. **Execution.** Apply Ch13's family-dependent rule: takers pay the spread (Ch12) and skip toxicity; makers earn the spread but face the toxicity diagnostic from Ch13 §3-§4.
5. **Regime conditioning.** Stratify the post-cost Sharpe by Ch15's vol-threshold and event-window detectors. Sharpe-by-regime is the "when does this family work?" question.

The pipeline is the *fairness instrument*. A family that fails any one checkpoint fails the chapter — not because the family is broken in principle, but because *on this data, through this pipeline*, it does not clear the bar that Ch12 set. A family that survives all five checkpoints is what §5.3 calls a "candidate" — promoted to Ch17-18 paper-trading, but with the wide-CI caveat still attached.

### Honest framing

The expected outcome is that *most* families fail, just as MR did. That outcome is not a chapter failure — it is exactly what a fair pipeline applied to a single 251-session window should produce. Real intraday edges are scarce; the production version of this exercise looks across symbols, decades, and asset classes before declaring a family alive. Ch17-18's paper-trading is the next checkpoint in that arc, not the final one.

### Cross-chapter links used in this chapter

- **Ch7 §3-§5** family definitions → instantiated in §2, §3, §4.
- **Ch7 §6** lag-120 hint → §2.1 empirical pursuit.
- **Ch7 §7** regime-change driver → §5.2 fingerprints.
- **Ch9-Ch13** pipeline → reused as the fairness instrument (above).
- **Ch10 §4** multiple-comparison discount → §5.3 Bonferroni accounting on the survivor.
- **Ch12** cost stack (round-trip ≈ 1.61 bp on QQQ at this notional) → §2.3, §3.4, §4.3.
- **Ch13** family-dependent execution → §2.4, §3.5.
- **Ch14** candidate-hunt promise (vol-targeting needs *something* with an edge to size) → §5.3 picks that candidate.
- **Ch15** regime indicators (vol-threshold §5.1, event-window §5.2) → §2.5, §3.6, §5.2.

## §2 — Momentum

### §2.1 Signal

Ch7 §6 reported an empirical curiosity: while lag-1 ρ on QQQ 1-min within-session log-returns runs negative (MR territory, the source of Ch8's signal), **at lag ≈ 120 minutes ρ flips positive at +0.0043, and at lag ≈ 240 the positive correlation strengthens slightly**. That is the Ch7 §6 hint this section pursues.

The full lag sweep on this chapter's window:

| Lag (min) | ρ |
|---:|---:|
| 1 | negative (Ch8 MR territory) |
| 5 | negative |
| 30 | negative |
| 60 | negative |
| **120** | **+0.0043** |
| **240** | **+0.0085** |

> **Snoop confession.** Pursuing a positive ρ at lag 120 *because* Ch7 §6 reported one is a form of in-sample selection. The lag sweep above evaluates several candidate lags and picks the one with the largest positive ρ. Ch10 §4's multiple-comparison discount applies to anything built on top of that pick. The chapter declares the snoop here and carries the cost forward to §5.3, where the survivor's Sharpe is Bonferroni-discounted by the full size of the parameter sweep that produced it.

The chapter's working pick is **(N=240, K=120)** — lookback 240 minutes, hold 120 minutes — chosen because lag-240 had the largest positive ρ in the sweep and 120 is half the lookback (a conventional shape: hold for "long enough to ride the signal, short enough that the signal stops applying").

**Signal rule.** Long entry when the trailing-N log return exceeds a vol-scaled threshold; short when it falls below the negative of the same threshold:

> r<sub>t, t−N</sub> > k<sub>σ</sub> · σ̂<sub>t</sub> · √(N / 60) → long
>
> r<sub>t, t−N</sub> < −k<sub>σ</sub> · σ̂<sub>t</sub> · √(N / 60) → short
>
> hold K minutes from entry, or until session close (whichever comes first)
>
> where:
> - r<sub>t, t−N</sub> = log-return from bar t−N to bar t (the N-minute trailing return at decision time t)
> - N = lookback in 1-min bars (chapter pick: N = 240)
> - K = hold horizon in 1-min bars (chapter pick: K = 120)
> - k<sub>σ</sub> = entry threshold multiplier — the cost-aware sweep parameter in §2.3
> - σ̂<sub>t</sub> = combined per-bar σ̂ at entry minute (this chapter uses a **rolling-20-day proxy** for tractability; the Ch15 §4 combined GARCH × seasonal estimator is the production-grade substitute)
> - √(N/60) = scaling factor that converts σ̂<sub>t</sub> (a per-bar quantity) to a per-N-minute scale, so the threshold has the same units as r<sub>t, t−N</sub>

The √(N/60) factor is the standard √-time vol scaling on a per-bar σ̂; it is what makes k<sub>σ</sub> dimensionless and comparable across choices of N.

### §2.2 Event-driven backtest

Ch9 §2's single-position event-driven loop drives the simulation: at each minute, if flat and the signal fires, enter; if in a position, check the K-bar timer and the session-close deadline; exit before the next entry is considered (the strict exit-before-entry order from Ch9 §2). All open positions are force-flattened at session close — no overnight risk on a 1-min intraday strategy.

The Ch9 §3 trade-level ledger records entry time, exit time, side, entry price, exit price, log-return, and `pnl_log`. The Ch9 §4 annualizer is `S = √(trades-per-year) · mean(pnl_log) / std(pnl_log)`.

**Result at the working pick (N=240, K=120, k<sub>σ</sub>=1.0)** — see notebook §2.2:

- Hit rate, profit factor, payoff ratio, per-trade mean/std all reported in the notebook trade-ledger summary.
- The headline read on the Ch9 §4 annualizer: **in-sample Sharpe is positive but small** — well inside the CI implied by N trades and a per-trade σ on the order of single bp.

### §2.3 Cost-aware k\* sweep

The Ch12 cost stack (round-trip ≈ 1.61 bp at this notional on QQQ) is subtracted from every trade. The signal-threshold parameter k<sub>σ</sub> is swept on {0.5, 0.7, 1.0, 1.3, 1.5, 1.8, 2.1, 2.5}.

**Headline numbers.**

- **Cost-naive k\* = 1.50, with S<sub>pre</sub> = +1.108.**
- **Cost-aware k\* = 1.50, with S<sub>post</sub> = +0.291.**

The cost wedge eats roughly **0.8 of the pre-cost Sharpe**, dropping the strategy from "interesting" to "marginal." The S<sub>pre</sub> vs S<sub>post</sub> surface is **non-monotonic, with twin peaks at k<sub>σ</sub> ≈ 0.7 and k<sub>σ</sub> ≈ 1.5**. The coincidence of cost-naive and cost-aware k\* at the same cell (1.50) is **fragile** — a small change to the cost assumption or to N/K would land them at different cells. Treat the coincidence as a data artifact, not a structural property of the strategy.

### §2.4 Execution choice

Momentum *takes* liquidity by hypothesis. The signal fires *because* the move is already happening; waiting for a passive fill at the same price the signal observed misses the move by definition.

> **Definition — family-dependent execution.** The rule of thumb that follows from Ch13's adverse-selection result: which order type is right depends on which way the strategy expects the market to move *after* the signal. Mean-reversion expects the market to come *to* the resting order, so makers earn the spread plus the reversion. Momentum and breakout-confirmation expect the market to move *away*, so passive fills happen only when the move stalls — exactly the trades the strategy doesn't want. Hence: MR makes (with the Ch13 toxicity caveat), momentum takes.

No toxicity simulation is run for momentum in this chapter — the family-dependent rule says taker, and Ch13's toxicity diagnostic applies only to maker variants. Spread is paid on entry and exit; commissions and impact are folded into the same Ch12 round-trip cost used in §2.3.

### §2.5 Regime conditioning

Sharpe is stratified by two Ch15 detectors:

- **Vol-threshold (Ch15 §5.1):** high-vol sessions are those whose σ̂<sub>GARCH</sub> exceeds the trailing-252 p80.
- **Event-window (Ch15 §5.2):** event sessions overlap the FOMC / CPI / NFP calendar (33 dates over the window, 29 of which land on RTH sessions).

> **Working hypothesis.** Momentum should look *cleaner* in low-vol / trending regimes (where moves persist) and worse in high-vol regimes (where vol spikes are typically followed by MR-style reversion, not continuation). Event-day momentum has both effects — fast information dump that *could* trend, plus a high-vol reversion risk.

The per-regime Sharpes for momentum are reported in the notebook §2.5 table. The **honest qualifier**: per-cell N drops to ~25-75 trades depending on the regime split, so per-cell Sharpe CIs are wide, and any sign-of-difference claim is descriptive, not statistical. The regime split is informative for "where does this family work?" planning, not for "is momentum *significantly* better in low-vol days?" inference.

### §2.6 Momentum — verdict

| Checkpoint | Sharpe |
|---|---:|
| IS, naive (best k<sub>σ</sub>) | +1.108 |
| Cost-aware (k<sub>σ</sub>\* = 1.50) | **+0.291** |
| Best regime-conditioned | (see notebook §2.5) |

**Verdict: marginal.** Momentum survives the cost wedge by a small positive margin (S<sub>post</sub> +0.291), but the CI around that point estimate dominates the point estimate itself — a chapter-window strategy with a few hundred trades has a Sharpe-CI on the order of ±0.5 around any point. The chapter does *not* call momentum a confirmed edge on this data; it calls it **a survivor of the cost bar that does not establish a robust positive Sharpe**.

## §3 — Opening-Range Breakout (ORB)

### §3.1 Signal

> **Definition — opening range (OR).** The price interval [low, high] traversed during the first N minutes of the RTH session. Conventional N is 30 minutes (the chapter default), motivated by Ch6 §4's finding that intraday vol's opening burst is roughly the first 30-minute window before reverting to a flatter midday level. Exercise 2 sweeps N ∈ {15, 30, 60}.

For each session, define:

> OR<sub>t</sub> = [min L over first 30 minutes, max H over first 30 minutes]
>
> long-break condition: 1-minute close > OR<sub>high</sub> · (1 + ε / 10⁴)
>
> short-break condition: 1-minute close < OR<sub>low</sub> · (1 − ε / 10⁴)
>
> where:
> - OR<sub>high</sub>, OR<sub>low</sub> = high and low of the first 30 minutes of the session
> - ε = padding in basis points; ε = 0 means "any break of the OR triggers", ε > 0 requires the close to clear the OR by ε bp (the gate against the **false break**)
> - the break condition is evaluated on **1-minute closes**, not on intra-bar highs / lows — the close confirms the break, avoiding the wick-only triggers that would inflate the false-break rate

> **Definition — false break.** A bar that crosses the OR boundary intra-bar (its high exceeds OR<sub>high</sub>, say) but closes *back inside* the range. The session does not, in retrospect, "break out"; the wick is microstructure noise, not directional information. ε > 0 and a close-based trigger together implement the standard false-break filter: the close has to clear the boundary plus a padding margin before the entry fires.

**OR width distribution on QQQ over this window:**

- Mean OR width: **50.5 bp**.
- p75 OR width: **72.2 bp** — the threshold that defines the "wide-OR" gate in §3.4.

Sessions with at least one break (long or short) over the working ε = 0 setting: **most sessions**; the empty-break sessions are those where the day's full range is narrower than 30-minute open range, which is rare.

### §3.2 Confirmation vs anticipation

The same breakout signal admits two distinct execution policies, with opposite implications for spread, fill certainty, and adverse selection:

> **Definition — confirmation variant.** Enter at the *close of the breaking bar* with a market order. Takes liquidity; pays the half-spread on entry. Fill certainty ≈ 1. The strategy waits for the break to be confirmed by a close-print before acting.

> **Definition — anticipation variant.** Post a *stop-limit* (a resting order combining a stop trigger with a limit price — the stop arms the order at the trigger; the limit caps the worst execution price) at OR<sub>high</sub> + ε bp (long) or OR<sub>low</sub> − ε bp (short) before any break has confirmed. The resting order rests on the book; the strategy *provides* liquidity. Earns the half-spread if filled. Fill certainty < 1 — a session whose range never breaks OR by ε bp produces no trade. Subject to the Ch13 toxicity diagnostic.

Hold rule, both variants: **until session close, single-shot per session per direction.** Each direction can fire at most once per session; once long-entered, a long re-fire on the same session is suppressed (and likewise for shorts). Both directions can fire on the same session if the price first breaks up and then breaks down (a "range trip" — rare on QQQ on this window).

### §3.3 Event-driven backtest

Both variants run through the Ch9 §2 event-driven loop. The trade-level ledger is the standard one. Per-variant baseline numbers (ε as noted):

| Variant | Trades | S<sub>pre</sub> | S<sub>post</sub> |
|---|---:|---:|---:|
| Confirmation, ε = 0, all sessions | **251** | **+0.308** | **−0.072** |
| Anticipation, ε = 5, all sessions | **250** | **−0.005** | **−0.389** |

The confirmation variant's pre-cost Sharpe is small but positive; the cost wedge (round-trip ≈ 1.61 bp, applied per trade) pushes it just under zero. The anticipation variant is essentially zero pre-cost — and that is *before* the toxicity diagnostic from §3.5, which makes it materially worse.

### §3.4 Cost-aware sweep — the 3 × 3 grid

For the confirmation variant, the cost-aware sweep is two-dimensional: OR-percentile gate × ε. The chapter sweeps **OR-percentile ∈ {25, 50, 75}** (only trade on sessions whose OR width exceeds the chosen percentile of the trailing OR-width distribution) × **ε ∈ {0, 5, 10} bp**. Nine cells. Apply Ch12 cost stack per trade. Print the 3 × 3 post-cost-Sharpe surface.

**Headline cell** — see notebook §3.3:

| Cell | Trades | S<sub>pre</sub> | S<sub>post</sub> |
|---|---:|---:|---:|
| **OR-p75 × ε = 10** | **59** | **+1.78** | **+1.41** |

This is the chapter's single positive cost-aware result. **Frame it carefully** — it is exactly the kind of "best of N cells" cell that Ch10 §4 warned about. §5.3 applies the Bonferroni discount.

Intuition for *why* this cell wins where ε = 0 fails:

- **OR-p75 gate** drops the days where the opening range is narrow — exactly the days where the "breakout" is most likely to be a chop print rather than a structural break. Narrow-OR days are the false-break factory.
- **ε = 10** raises the bar another 10 bp above the OR boundary, which on QQQ is roughly the average half-spread plus a comfortable noise margin. The combination filters down to 59 trades over 251 sessions — about one trade every 4-5 sessions — but those 59 are the *cleanest* breaks in the sample.

### §3.5 Execution — take vs make depends on the variant

For the anticipation variant, the Ch13 §3-§4 toxicity diagnostic is the relevant test. **Toxicity** = mean unconditional drift − mean filled drift (in bp; see Ch13 Definition).

> **Empirical result for anticipation, ε = 5: toxicity ≈ +1.82 bp.**

That is **larger than the half-spread Ch12 estimated (≈ 0.72 bp)** — the rebate the anticipation variant earns by posting passively is wiped out, and then some, by adverse selection. Filled trades are systematically worse than unfilled. **The anticipation variant destroys alpha.**

For the confirmation variant, the family-dependent rule says taker: pay the spread on entry, accept fill certainty, skip the toxicity diagnostic. The confirmation variant's S<sub>post</sub> already includes the spread cost (via the Ch12 round-trip stack); no additional toxicity adjustment applies. **Confirmation takes; anticipation makes and gets toxified.**

### §3.6 Regime conditioning

Stratify the cost-aware S<sub>post</sub> by Ch15 regime detectors, separately for each variant:

- **Vol-threshold (Ch15 §5.1):** high-vol vs low-vol sessions.
- **Event-window (Ch15 §5.2):** event vs non-event sessions.

> **Working hypothesis.** Breakout should work *better* in high-vol / event-day regimes — those are the days with enough directional energy to sustain a break past the false-break gate. Low-vol chop is where breakouts fail by construction.

Notebook §3.5 reports the per-regime conditional Sharpes. **Honest small-N qualifier:** per-cell N for the wide-OR gate is on the order of 15-30 trades after regime conditioning; differences of order ±0.5 in conditional Sharpe are not statistically distinguishable from noise. The conditional Sharpes are **descriptive** evidence about *where* breakouts work, not statistical confirmation that they *do*.

### §3.7 Breakout — verdict per variant

| Variant | IS Sharpe | Cost-aware | Notes |
|---|---:|---:|---|
| Confirmation, all sessions, ε=0 | +0.308 | −0.072 | Fails the cost bar by a hair. |
| Anticipation, ε=5 | −0.005 | −0.389 | Toxicity (+1.82 bp) larger than rebate. Destroys alpha. |
| **Confirmation, OR-p75, ε=10** | **+1.78** | **+1.41** | **Positive cost-aware Sharpe — single survivor across all variants. See §5.3 for the Bonferroni discount.** |

## §4 — Event-driven (FOMC pre/post drift)

The event-driven family is, in principle, the cleanest of the four: scheduled releases produce information bursts at known times, and a strategy keyed to the calendar trades only when the macro DGP changes. In practice on this window, the family's pain point is **sample size**.

### §4.1 Signal

The chapter focuses on FOMC (Federal Open Market Committee rate-decision releases, ~14:00 ET — the highest-attention release; CPI = Consumer Price Index and NFP = Nonfarm Payrolls are deferred to Exercise 3; see Ch15 §5.2 for full release-mechanics gloss on all three). Each FOMC session has three windows:

- **Pre-window:** minutes 240-299 (12:30 PM ET – 1:29 PM ET) — the hour leading up to release.
- **Release-window:** minutes 300-329 (1:30 PM ET – 1:59 PM ET).
- **Post-window:** minutes 330-389 (2:00 PM ET – 3:00 PM ET) — the hour after release.

(Note: FOMC's policy decisions actually print at 2:00 PM ET. The chapter's window split is offset relative to nominal release time for arithmetic convenience and consistency with Ch6's minute indexing; "release-window" and "post-window" labels are descriptive rather than exact pre/post-print partitions. The hypothesis structure is unaffected.)

Two hypotheses:

> **Definition — pre-release drift (H1).** The hypothesis that sign(pre-window return) predicts the sign of the release-window return. Mechanism: positioning flow ahead of a known information event leaves a small directional residue that continues into the release.

> **Definition — post-release continuation (H2).** The hypothesis that sign(release-window return) predicts the sign of the post-window return. Mechanism: information takes time to fully propagate; the initial release-window move continues, on average, into the next hour.

**Sample.** The calendar has **9 FOMC dates** in window; **8** have complete pre / release / post slots on RTH sessions (one date has incomplete data). **N = 8 is the operative sample size for both hypotheses.**

> **Foot-gun — N = 8 is not a statistical sample.** Sharpe is `√(tpy) · mean / std`; on N = 8 the denominator (a sample std) is itself a tiny-sample statistic with a wide CI. The standard finite-sample correction is that t-stats on N = 8 require values of `|t| ≈ 2.36` for two-sided 5% significance (degrees of freedom = 7), whereas the asymptotic threshold is `|t| ≈ 1.96`. The chapter does not need to invoke a precise finite-sample p-value to make the point: every Sharpe reported in this section has a bootstrap CI that **dwarfs the point estimate**. Read the CI before reading the sign.

### §4.2 Event-driven backtest

One trade per hypothesis per FOMC session. H1 enters at the end of the pre-window and exits at the end of the release-window; H2 enters at the end of the release-window and exits at the end of the post-window. Total trade count = **8 + 8 = 16** across both hypotheses.

The notebook prints the per-FOMC table (date × pre / release / post returns × H1 PnL × H2 PnL).

### §4.3 Cost-aware

Per-trade cost subtraction: each trade pays the Ch12 round-trip cost of **1.61 bp**. Post-cost Sharpes (annualized via the Ch9 √(tpy) factor):

| Hypothesis | S<sub>post</sub> |
|---|---:|
| H1 (pre-release drift) | **−9.50** |
| H2 (post-release continuation) | **−5.17** |

The annualization factor for an 8-trade-per-year strategy makes the Sharpe magnitudes look extreme. **Do not read the magnitude as economic effect size.** Read the CI in §4.5.

### §4.4 Execution choice

Event-driven takes the immediate post-release move; the family-dependent rule is "taker on the entry minute" (same logic as momentum — the move is happening when the signal fires; resting orders would be filled into the move). With **1-min bars** as the simulation resolution and **N = 8 sessions**, execution-choice nuance is below the CI width of the headline result. The chapter notes the rule, applies the spread cost (already in the §4.3 round-trip), and defers maker / taker comparison to Exercise 3, which expands N to ~24 by adding CPI and NFP.

### §4.5 Sample-size honesty

Bootstrap 95% CI on each hypothesis's Sharpe, 1000 resamples (see notebook §4.2):

| Hypothesis | Point estimate (S<sub>post</sub>) | Bootstrap 95% CI |
|---|---:|---|
| H1 | −9.50 | **(−41.6, +2.1)** |
| H2 | −5.17 | **(−25.7, +7.1)** |

The CI for H1 spans **+44 Sharpe units**; the point estimate is −9.50. The CI for H2 spans **+33 Sharpe units**; the point estimate is −5.17. **The CI dwarfs the point estimate, and the upper end of both CIs is comfortably positive.** Under standard inference, neither hypothesis is statistically distinguishable from zero — and certainly neither can be *rejected* as positive.

The honest conclusion is **not** "H1 and H2 are negative on QQQ FOMC." It is **"N = 8 is too small to support a verdict in either direction."** Exercise 3 extends the same analysis to FOMC + CPI + NFP for ~24 events combined; that is the actual test.

### §4.6 Event-driven — verdict

**Named, demonstrated, deferred.** The event-driven family is *built* in this chapter: signal, backtest, cost stack, regime hook, sample-size honesty. The family does *not* produce a usable point estimate on N = 8. Do not paper-trade event-driven on this evidence. Exercise 3 is the next instrument.

## §5 — Cross-family comparison

### §5.1 Side-by-side deflation table

The notebook §5.1 assembles the cross-family table. All four families on identical checkpoints:

| Row | Family / variant | IS S<sub>pre</sub> | Cost-aware S<sub>post</sub> | Notes |
|---|---|---:|---:|---|
| 1 | MR (Ch8 §1 → Ch13 §6) | **+2.080** | **−1.110** | Cost stack kills it; Ch13 maker rescue fails to toxicity. |
| 2 | Momentum, N=240, K=120, k<sub>σ</sub>=1.50 | +1.108 | +0.291 | Marginal survivor; wide CI. |
| 3 | Breakout-confirm, all sessions, ε=0 | +0.308 | −0.072 | Fails by a hair. |
| 4 | Breakout-anticipate, ε=5 | −0.005 | −0.389 | Toxicity +1.82 bp; alpha-destroyer. |
| 5 | **Breakout-confirm, OR-p75, ε=10** | **+1.78** | **+1.41** | **Single positive cost-aware result.** Bonferroni in §5.3. |
| 6 | Event-driven H1 (FOMC pre-release) | n/a (N=8) | −9.50 | CI (−41.6, +2.1); no verdict. |

The MR row's S<sub>pre</sub> of +2.080 and S<sub>post</sub> of −1.110 are the Ch8 §1 / Ch13 §6 anchor — the same numbers Ch12 §4 and Ch13 §6 quoted. The cost wedge eats ~3.2 Sharpe units of MR; the analogous wedge eats ~0.4 Sharpe units of breakout-confirm-p75-ε10. Both pre-cost numbers look promising; only one post-cost number survives.

### §5.2 Regime fingerprints

The family × regime Sharpe heatmap (notebook §5.2) puts strategy on rows, regime on columns. Working hypotheses (from Ch7 §7 and the family mechanisms):

- **MR best in high-vol** — vol spikes are reversion-prone; MR feeds on reversion.
- **Momentum best in trending / low-vol** — trends require quiet enough background vol that the signal isn't overwhelmed by noise.
- **Breakout best on event days** — event days have the directional energy to sustain a break past the false-break gate.

The heatmap colors will show *some* of these patterns and *not all* of them. **Honest qualifier:** per-cell N is small (typically 15-60 trades after regime conditioning) and per-cell Sharpe CIs accordingly wide. Differences across cells of order ±0.5 are descriptive, not statistically distinguishable from noise. The fingerprints **suggest** the regime mapping above; they do not **prove** it on this window.

The regime-fingerprint framing matters operationally because of the §6 third decision rule: a strategy that works only in one regime can in principle be combined with one that works only in another. Exercise 4 builds that combination.

### §5.3 Pick the candidate for Ch17-18

The chapter's verdict landed in the spec's "likely case": **one survivor**.

> **Survivor:** ORB-confirm × OR-p75 × ε=10, **S<sub>post</sub> = +1.41 on N = 59 trades** (notebook §3.3 headline cell).

#### Deflate honestly — Bonferroni accounting

The survivor was selected from a **9-cell 2D sweep** (3 OR-percentiles × 3 ε values, §3.4). Ch10 §4's standard discount for "best of N cells" is **Bonferroni**:

> **Rule — Bonferroni on a parameter sweep.** Divide the t-stat of the surviving cell by √N<sub>cells</sub>, where N<sub>cells</sub> is the number of cells evaluated. Equivalently, scale the surviving Sharpe by 1 / √N<sub>cells</sub>.
>
> where:
> - N<sub>cells</sub> = total number of (parameter, value) cells the analyst evaluated to find the survivor (here, 9)
> - Sharpe scaling follows from `t-stat = Sharpe · √(N<sub>trades</sub> / tpy)` being linear in Sharpe, so a √N<sub>cells</sub> haircut on t-stat is a √N<sub>cells</sub> haircut on Sharpe

For this survivor: **discounted Sharpe ≈ +1.41 / √9 = +0.47.**

**The headline +1.41 is not the operational estimate.** **+0.47 is**, and even +0.47 has a wide CI on N = 59 — a back-of-envelope CI half-width on N = 59 trades with per-trade σ on the order of 10 bp is itself on the order of ±0.5 Sharpe units. The post-discount estimate is **statistically indistinguishable from zero** by the chapter's own evidence.

#### Ship to Ch17-18 paper-trading — with caveat

The candidate is promoted to Ch17-18 paper-trading. The reason is **not** that +0.47 is a confirmed edge — it is not. The reason is the third decision rule from §6: **a candidate that survives the discount, even with wide CI, is the only thing on the shelf worth running on live futures mechanics**. Ch17-18 paper-trades it primarily as **discipline practice** — the act of running a candidate through tick-size, margin, kill-switch, and order-management mechanics teaches the production half of the pipeline, regardless of whether the candidate ends up profitable.

#### Pre-state the expected live outcome

The honest pre-deployment forecast: **the live Sharpe is more likely to land in [0, +0.5] than at the IS +1.41**, and may well land at zero or below. If it lands at zero, that is **the expected outcome under the deflation arc**, not a failure mode. Ch17-18 is calibrated to that expectation: the kill switch trips at deterioration thresholds calibrated to "we expected this; here is the line at which we stop."

## §6 — So what

Three decision rules carry forward from this chapter:

1. **Run new strategies through the same pipeline that deflated your first.** Pipeline *consistency* matters more than any single result. A fresh family compared to MR through a different pipeline tells you nothing about whether the family is real; it tells you about pipeline differences. Use the same five checkpoints, in the same order, with the same cost assumptions, every time.
2. **Execution choice is family-dependent.** Momentum takes (it must — the move is happening when the signal fires). MR makes, or makes-with-care per Ch13 (the move is *about* to reverse to your fill). Breakout depends on the variant: confirmation takes (post-confirmation, the move is happening) and anticipation makes-and-gets-toxified (the resting limit fills exactly when the break is failing). Match the order type to the family's *direction of expected move*, not to your spread-cost preference.
3. **Regime fingerprints matter more than overall Sharpe.** A strategy that works only in one regime can in principle be combined with one that works only in another. Exercise 4 builds that combination directly (MR on low-vol days, ORB survivor on high-vol days). **It does not survive Bonferroni either** — the gate-selection itself is a multiple-comparison step, and the combination's Sharpe (raw +0.05; gate-discounted +0.035) is well inside its CI. The framework matters; the worked-example numbers are method evidence, not deployment evidence.

### What this chapter cannot yet tell you

- **Futures-contract mechanics.** Tick size, contract multiplier, margin, overnight handling, regular vs E-mini distinctions — none of which apply to a 1-min QQQ ETF backtest. Ch17 owns this.
- **NQ tick size and exchange fee structure.** NQ (E-mini Nasdaq-100 futures) is the natural production vehicle for an intraday Nasdaq-100 strategy because of its capital efficiency and 23-hour session. Its tick size, point value, and fee schedule change every per-trade cost in this chapter. Ch17 owns this.
- **Going-live order management.** Kill switches, position reconciliation, latency monitoring, fill-quality TCA — all the production scaffolding that turns a backtest into a deployed strategy. Ch17-18 own this.

## Key Terms

| Term | Definition |
|---|---|
| **Momentum** | A strategy family that bets on continuation of the most recent move. Operationally: enter when the trailing-N return exceeds a vol-scaled threshold; hold K minutes. Ch7 §6's positive lag-120 ρ is the hint this chapter pursues. |
| **Opening range (OR)** | The price interval [min L, max H] traversed during the first 30 minutes of the RTH session. The reference range whose break the ORB family trades. Mean width on QQQ on this window: 50.5 bp; p75: 72.2 bp. |
| **Breakout confirmation** | An ORB execution variant that enters at the *close* of the breaking bar with a market order. Takes liquidity; pays the spread on entry; fill certainty ≈ 1. The variant whose OR-p75 × ε=10 cell is the chapter's single positive cost-aware result. |
| **Breakout anticipation** | An ORB execution variant that posts a stop-limit at OR<sub>high</sub> + ε bp (long) or OR<sub>low</sub> − ε bp (short) before the break confirms. Makes liquidity; earns the spread when filled; subject to Ch13 toxicity. On this data toxicity (+1.82 bp) exceeds the rebate (~0.72 bp). |
| **False break** | A bar that crosses the OR boundary intra-bar but closes back inside. The wick is microstructure noise, not directional information. Filtered by requiring close-based triggers and ε > 0 padding. |
| **Event-driven strategy** | A family that trades around scheduled releases (FOMC, CPI, NFP) on the assumption that pre-release positioning or post-release information propagation creates predictable short-window drift. Pain point on a single-symbol single-year window: sample size. |
| **Pre-release drift (H1)** | The event-driven hypothesis that sign(pre-window return) predicts sign(release-window return). Mechanism: positioning flow ahead of a known event leaves a directional residue. Bootstrap CI on QQQ FOMC N=8: (−41.6, +2.1) — no verdict. |
| **Post-release continuation (H2)** | The event-driven hypothesis that sign(release-window return) predicts sign(post-window return). Mechanism: information propagation continues the initial move. Bootstrap CI on QQQ FOMC N=8: (−25.7, +7.1) — no verdict. |
| **Regime fingerprint** | The family × regime Sharpe heatmap. Reads "where does this family work?" rather than "is this family good on average?". Useful for combination logic (Exercise 4); fragile to per-cell N. |
| **Family-dependent execution** | The rule that the right order type depends on the family's expected post-signal move direction. MR makes (move reverses to fill); momentum and breakout-confirmation take (move is in progress); breakout-anticipation makes and gets toxified (resting limit fills when break fails). Derived from Ch13 §3-§4. |

## Up next

**Ch17 — Futures mechanics and NQ.** The candidate from §5.3 (ORB-confirm × OR-p75 × ε=10) is currently defined on QQQ 1-min ETF bars. NQ — the E-mini Nasdaq-100 futures contract — is the production deployment vehicle: ~23-hour session, point value $20/point, near-zero financing carry, capital-efficient margin. Ch17 maps the strategy onto NQ tick mechanics and rebuilds the cost stack from contract-level commissions and exchange fees.

**Ch18 — Paper-trading the survivor.** Live-ledger paper-trade with kill switches calibrated to the §5.3 deflation forecast. The point of paper trading is *not* to confirm a +1.41 edge — the chapter has already told you that estimate is not operational. The point is to run the production-management half of the pipeline (kill switches, ledger reconciliation, fill-quality TCA) on a candidate that the deflation arc says might land anywhere in [−0.5, +0.5]. Whatever the live Sharpe is, the discipline is the deliverable.

## Exercises

1. **SPY transfer of the best-surviving family.** Re-run the
   Breakout-confirm × OR-p75 × ε=10 variant on SPY (load
   `06-bridge-to-intraday/data/spy_1min.parquet` if it exists; else
   load SPY via yfinance for the same window). Document the
   Sharpe gap and discuss why.

2. **ORB sensitivity to opening-range length.** Run §3 at
   OR-window ∈ {15, 30, 60} minutes. Apply Bonferroni across the
   9 candidate parameter combinations (3 windows × 3 ε values).
   Discuss the Ch10 §4 snooping inflation.

3. **Event-driven extended to CPI and NFP.** Re-run §4 across all
   three event types (FOMC + CPI + NFP). Does ~24 events instead of
   ~8 narrow the bootstrap CI enough for a verdict?

4. **Regime-gated combination.** Use Ch15 regime indicators to switch
   between MR (Ch11) and the best §2/§3/§4 family. Does the gated
   combination Sharpe beat either alone, after costs? Apply Ch10-style
   multiple-comparison discount on the gate-selection itself.
