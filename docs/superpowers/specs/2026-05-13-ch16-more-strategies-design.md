# Chapter 16 Design — More Strategies: Momentum, Breakout, Event-Driven

**Date:** 2026-05-13
**Status:** Approved (Part 8 closer; final pre-futures chapter).
**Spine:** Ch7 named four strategy families. Ch8-13 ran one of them (intraday MR) through a full honest pipeline and closed at after-execution Sharpe −1.11. Ch16 runs the other three families through the same pipeline. The question: does *any* non-MR family on this data survive the Ch12 cost bar? Honest expected answer: most don't. Pick the least-bad as Ch17-18's working candidate, with explicit caveats where the verdict is "not statistically distinguishable from zero."

## Why this chapter exists

The curriculum's biggest cross-chapter promise lives here. Five chapters point to Ch16:

- **Ch7 §promise:** "Ch16 builds runnable instances of momentum, breakout, event-driven (Ch7 §3-5)."
- **Ch12 §promise:** "Each new family must clear the Ch12 cost bar. The expected outcome: most fail; the survivors are the search target."
- **Ch13 §promise:** "Execution choice is family-dependent — momentum wants to take (signal IS the move); MR wants to make; breakout depends on front-run vs confirm."
- **Ch14 §promise:** "Ch16 will hunt for a real positive-EV strategy that survives the Ch12-13 cost/execution bar."
- **Ch15 §promise:** "Ch16 uses §5 regime indicators as conditioning variables for 'when does each strategy family work?'"

The Ch8-13 arc proved the pipeline works as a fairness instrument; Ch16 proves it generalizes across strategy families. The chapter also produces the candidate Ch17-18 will paper-trade.

## Three-flavor framing

Three families, each runnable end-to-end through the compressed Ch9-13 pipeline:

1. **Momentum.** Trailing N-min momentum on QQQ — sign-flipped mirror of Ch8's MR. Empirical hook: Ch7 §6 lag-120 ρ = +0.004 (positive, tiny).
2. **Breakout.** Opening Range Breakout (ORB). Two execution variants: confirmation (take after break) vs anticipation (post at range edge before break).
3. **Event-driven.** FOMC pre/post drift on the ≤8 FOMC sessions in the Ch11 window. Sample-size honesty is the headline.

Each family gets the same five-step pipeline: signal → backtest → cost-aware k\* → execution choice → regime conditioning. The chapter's payoff is the cross-family comparison in §5.

## Section structure

### §1 — Setup: the four families, side by side

Recap Ch7's four families (MR, momentum, breakout, event-driven) and their proposed mechanisms. State the chapter's question: does any non-MR family survive Ch12-13's cost+execution bar on this data? Map the Ch8-13 pipeline onto a five-step checklist that each family will be run through:

1. Signal — define and validate it empirically (lag-k autocorr, range stats, event drift)
2. Backtest — event-driven, point-in-time, vol-aware (`feedback`: inherit Ch9 §2 loop)
3. Cost-aware k\* — Ch12 round-trip cost stack, swept across thresholds
4. Execution — Ch13 toxicity diagnostic for take vs make choice
5. Regime conditioning — Ch15 indicators as conditioning variables

Up-front honest framing: most families are expected to fail. The verdict matters less than the *pipeline as fairness instrument*.

### §2 — Momentum (trailing N-min)

#### §2.1 — Signal

Empirical hook: Ch7 §6 reported lag-120 ρ = +0.004 (positive but tiny). Run the lag sweep on the Ch11 window (1-min QQQ, 95k bars). Report lag-k ρ for k ∈ {1, 5, 30, 60, 120, 240, 390}. Disclose this as a snooping search and forward-point to §2.4 Bonferroni.

Choose (N, K) — momentum's mirror of Ch8's MR (N, K). Working pick: pick the largest |ρ| at positive sign. Plan target: lag-120 region, N ≈ 60-120, K ≈ 30-60. Disclose as snooping; if mid-execution surprise mirrors Ch8's "(5, 5) loses; (1, 3) wins," update §2 narrative accordingly.

**Signal rule.** Long entry when r_{t, t-N} > k_σ · σ̂_t · √(N/60); short when r_{t, t-N} < −k_σ · σ̂_t · √(N/60). Hold K minutes or until end of session, whichever comes first. Where-clauses on N, K, k_σ, σ̂_t (uses Ch15 §4 combined estimator).

#### §2.2 — Event-driven backtest

Single-position event-driven loop from Ch9 §2 (~50 lines, exit-before-entry order, force-flatten at session end). Trade-level ledger. Annualized Sharpe with √(tpy) factor from Ch9 §4.

Report:
- Trade count, hit rate, profit factor, payoff ratio
- Per-trade mean / std in bp
- Annualized Sharpe (in-sample on Ch11 window — no train/test split yet; that's §2.4 walk-forward equivalent)

#### §2.3 — Cost-aware k\* sweep

Sweep k_σ ∈ {0.5, 0.7, ..., 2.5} per Ch12 §6. Apply Ch12's full cost stack (Roll's spread + IBKR commission + impact at $30k Q). Plot pre-cost and post-cost Sharpe vs k_σ on the same axes. Report cost-naive k\* (argmax of pre-cost) and cost-aware k\* (argmax of post-cost).

Expected outcome: momentum's edge per trade is small (consistent with the tiny lag-k ρ). 1.6 bp round-trip cost likely dominates. Cost-aware k\* may be far from cost-naive — or both may be negative.

#### §2.4 — Execution choice

Momentum **takes** liquidity by hypothesis: when the signal fires, the move is already happening, and waiting for a passive fill means missing the move. Honor Ch13's family-dependent execution claim: momentum's signal IS the move.

Demonstrate the asymmetry: run a passive-entry simulation (Ch13 §3 fill rule). Expected outcome: fill rate low *and* unfilled-bucket drift in strategy direction is large (the cleanest possible toxicity result). The taker baseline beats the maker variant.

Brief Ch13 toxicity diagnostic table for completeness.

#### §2.5 — Regime conditioning

Compute momentum Sharpe conditional on each Ch15 regime indicator:
- §5.1 vol-threshold: high-vol vs low-vol
- §5.2 event-window: event days vs non-event days
- §5.3 HMM: smoothed high-vol-state probability bucketed

Plot the conditional Sharpes side by side. Does momentum work better in any regime? Plan working hypothesis: momentum should be cleaner in trending / low-vol regimes; mean-reversion-prone in high-vol. Disclose as a hypothesis to be tested.

#### §2.6 — Family verdict

Per-family deflation table (mirrors Ch11 §7 and Ch13 §6):

| Stage | Sharpe |
|-------|--------|
| In-sample, no cost | ... |
| Event-driven, next-open | ... |
| Cost-aware k\* | ... |
| Best regime-conditioned | ... |

Verdict line: survives / borderline / fails the cost bar.

### §3 — Breakout (Opening Range Breakout)

#### §3.1 — Signal

Define the opening range OR_t as [low, high] of the first 30 minutes (minutes 0-29 of session t). Define a break above when 1-min close > OR_high, break below when 1-min close < OR_low.

Range stats on Ch11 window:
- Mean OR width in bp
- OR-width distribution by Ch15 regime
- Fraction of sessions with at least one break

Where-clauses on OR_high, OR_low, and the break condition.

#### §3.2 — Confirmation vs anticipation

Two execution variants on the same signal:

- **Confirmation.** Enter at the close of the first 1-min bar where break is confirmed. Take liquidity.
- **Anticipation.** Post a stop-limit at OR_high + ε bp (long) / OR_low − ε bp (short) before the break. Provide liquidity (technically: the broker holds the stop, but the limit-leg pricing matters).

Define both rules and stop / hold conventions: hold until session close, or until reverse break, or until K minutes pass — whichever comes first. Working pick: hold until session close (single-shot per session per direction).

#### §3.3 — Event-driven backtest

Run both variants on Ch11 window. Trade-level ledger per variant.

#### §3.4 — Cost-aware k\*

For breakout, the parameter sweep is OR-width-bin × ε threshold, not a single k_σ. Run a coarse 2D sweep over OR-percentile buckets {p25, p50, p75} × ε ∈ {0, 5, 10} bp. Apply Ch12 cost stack. Plot Sharpe surface.

#### §3.5 — Execution: take vs make depends on the variant

Confirmation variant: takes. Subject to Ch12 spread cost on entry.
Anticipation variant: makes. Subject to Ch13 toxicity — when the stop-limit fills, was the break clean or a false-break that immediately reverses?

Run the Ch13 toxicity decomposition on the anticipation variant:
- Filled-bucket mean return
- Unfilled-bucket drift in strategy direction
- Strict-toxicity formula

Expected outcome: anticipation has the canonical false-break problem; confirmation pays the spread on each entry. The trade-off is interesting whichever way it goes.

#### §3.6 — Regime conditioning

Conditional Sharpe per variant per Ch15 regime. Working hypothesis: breakouts work in high-vol / event-day regimes (where OR width is large enough to give the break momentum) and fail in low-vol / chop regimes.

#### §3.7 — Family verdict

Per-family deflation table, both variants. Verdict line.

### §4 — Event-driven (FOMC pre/post drift)

#### §4.1 — Signal

FOMC release at 2:00 PM ET. Define three windows:
- **Pre-window.** Minutes 240-299 (12:00-12:59 PM) — pre-release positioning
- **Release-window.** Minutes 300-329 (1:00-1:29 PM) — bracketing release
- **Post-window.** Minutes 330-389 (1:30-2:29 PM) — post-release continuation

Two signal hypotheses:
- **Pre-release drift.** Direction of pre-window return predicts release-window direction (positioning leaks).
- **Post-release continuation.** Direction of release-window return predicts post-window direction (momentum on news).

Compute both on Ch11 window's FOMC sessions (8 expected). Honest sample-size flag up front: 8 observations is not a statistical sample — every number reported here has a CI wider than the point estimate.

#### §4.2 — Event-driven backtest

Single trade per FOMC session per hypothesis. Run both. Total trade count ≤ 16 across both hypotheses.

#### §4.3 — Cost-aware

Per-trade cost stack identical to Ch12. With ≤8 trades per hypothesis, per-trade mean noise dominates; cost subtraction is mechanical.

#### §4.4 — Execution choice

Event-driven typically takes the immediate move and posts for the fade. With 1-min bars and only 8 observations, the execution choice doesn't materially change the bootstrap CI width. Document the framework; defer empirical comparison.

#### §4.5 — Sample-size honesty

Bootstrap CI on event-driven Sharpe. Expected CI width: ±2.5 or wider (Ch11-class wide). Headline finding likely "the point estimate is suggestive but the CI dwarfs the difference from zero — extending to CPI and NFP is Exercise 3."

#### §4.6 — Family verdict

Deflation table where applicable. Verdict line probably "named, demonstrated, deferred to a longer-data-window followup or larger event set."

### §5 — Cross-family comparison

#### §5.1 — Side-by-side deflation table

All four families (MR included, summarized from Ch11/13) at the same checkpoints. Single table:

| Family | IS Sharpe | OOS / event-driven Sharpe | Cost-aware Sharpe | Verdict |
|--------|-----------|---------------------------|-------------------|---------|
| MR (Ch8-13) | +2.08 | +0.88 | −1.11 | Don't trade |
| Momentum (§2) | ... | ... | ... | ... |
| Breakout-confirm (§3) | ... | ... | ... | ... |
| Breakout-anticipate (§3) | ... | ... | ... | ... |
| Event-driven (§4) | ... | ... | ... | ... |

#### §5.2 — Regime fingerprints

Heatmap: family Sharpe (rows) × Ch15 regime indicator (columns). Working hypothesis from Ch15-prep:
- MR best in high-vol (Ch7 §6 already found 2× lag-1 in closing window)
- Momentum best in trending regimes
- Breakout best on event days
- Event-driven by definition only on event days

Numbers fill the cells in execution. Honest qualifier: small N per cell makes most differences noise.

#### §5.3 — Pick the candidate for Ch17-18

Honest verdict. Three possible outcomes pre-stated:
- **Best case.** One family produces a positive cost-aware Sharpe with a CI that doesn't straddle zero too badly. Ship that to Ch17-18.
- **Likely case.** No family clearly beats the bar but one (probably breakout-confirm or regime-gated MR) has the least-negative cost-aware Sharpe. Ship it with explicit "still not statistically distinguishable from zero" caveat. Ch17-18 paper-trades it primarily as a discipline lesson.
- **Worst case.** All families fail explicitly. Ch17-18 reframes as "paper-trade the discipline, not the edge" with a clean negative result.

The chapter is written to land cleanly in any of the three outcomes — the value is the framework, not the specific verdict.

### §6 — So what + Key Terms + Up next

**So what?** Three decision rules:
1. Run new strategies through the *same* pipeline that deflated your first one. Pipeline consistency matters more than any single result.
2. Execution choice is family-dependent. Don't reuse Ch8's market-order template for momentum (where you'd be too slow) or for breakout-anticipate (where you need to be on the book before the break).
3. Regime fingerprints matter more than overall Sharpe. A strategy that works only in high-vol regimes can be combined with one that works only in low-vol regimes — Exercise 4 explores the combination.

**What this chapter can't yet tell you:** futures-contract mechanics, NQ tick size, exchange fee structure, going-live order management. That's Ch17-18.

**Key Terms (target 10).** Momentum, opening range, breakout confirmation, breakout anticipation, false break, event-driven strategy, pre-release drift, post-release continuation, regime fingerprint, family-dependent execution.

**Up next.** Ch17 takes the chosen candidate to NQ futures mechanics (tick size, contract specs, margin, exchange fees). Ch18 paper-trades it.

## Data

Reuses Ch6 QQQ 1-min parquet (Ch11 window, 251 RTH sessions, 95k bars).
Reuses Ch15 event_calendar.csv (FOMC, CPI, NFP).
Reuses Ch15 σ̂_t combined estimator and regime indicators (importable from Ch15 notebook helpers).
No new external pulls.

## Dependencies

All reused from Ch6-15. No new packages.

## Exercises

1. **SPY transfer of the best-surviving family.** Re-run §2/§3/§4 (whichever survived) on SPY. Document the Sharpe gap and discuss why.
2. **ORB sensitivity to opening-range length.** Run §3 at OR-window ∈ {15, 30, 60} min. Apply Bonferroni. Snooping demo per Ch10 §4.
3. **Event-driven extended to CPI and NFP.** Re-run §4 across all three event types. Does ~24 events instead of ~8 narrow the CI enough for a verdict?
4. **Regime-gated combination.** Use Ch15 regime indicators to switch between MR (Ch11) and the best §2/§3/§4 family. Does the gated combination Sharpe beat either alone, *after costs*? Apply Ch10-style multiple-comparison discount on the gate-selection itself.

Worked solutions for Exercises 1 and 4 in the lesson notebook; 2 and 3 stay as prompts only. (Exercise 4 in particular is meaty — equivalent to a mini Ch11 walk-forward on the gate parameter.)

## Promises honored

- **Ch7 §promises** to build runnable momentum, breakout, event-driven — paid in §2, §3, §4 respectively.
- **Ch7 §6** lag-120 = +0.004 hint — empirically pursued in §2.1.
- **Ch7 §7** edge-decay drivers — regime-change driver re-paid in §5.2 fingerprints.
- **Ch12 §promise** "each family must clear the Ch12 cost bar; most fail" — paid in §2.3, §3.4, §4.3, §5.1.
- **Ch13 §promise** family-dependent execution — paid in §2.4 (momentum takes), §3.5 (breakout-anticipate makes), §4.4 (event-driven both).
- **Ch14 §promise** "Ch16 hunts for a real positive-EV strategy" — paid in §5.3, with all three pre-stated outcomes.
- **Ch15 §promise** regime indicators as conditioning variables — paid in §2.5, §3.6, §4.4, §5.2.

## Promises to honor in later chapters

- **Ch17** takes §5.3's candidate to NQ futures mechanics. The cost stack changes (CME fees differ from IBKR equity commissions; tick size is a hard discreteness constraint; overnight margin matters even for sub-session strategies).
- **Ch18** paper-trades the candidate. The Ch15 regime indicators become live monitoring inputs. The candidate's regime fingerprint becomes a real-time risk dashboard.

## Pedagogical notes

- **Concept before statistics** (`feedback_concept_before_statistics`): each family's §x.1 names the *concept* (what is momentum / breakout / event-driven, in trader's language) before any formula. §5.3 verdict frames the result in dollars and decisions, not just Sharpe numbers.
- **Define every term on first use** (`feedback_define_every_term`): "opening range," "false break," "pre-release drift," "regime fingerprint," "family-dependent execution" all get inline glosses + Key Terms entries.
- **Define every formula's symbols** (`feedback_define_formula_symbols`): the momentum entry rule, the OR_high/OR_low break condition, and any conditional-Sharpe formulas carry where-clauses.
- **Push interpretations past description** (`feedback_push_interpretations_past_description`): every family verdict in §x.6 connects to dollars (what a $30k position made or lost across N trades) and to mechanism (what about the family's hypothesized mechanism survived the empirics).
- **No external knowledge leaps** (`feedback_no_external_knowledge_leaps`): FOMC, CPI, NFP each get scale + release-mechanics glosses at first use (reused from Ch15 if same file structure; otherwise re-stated). "Stop-limit," "false break," and any new order-book vocabulary get inline definitions.
- **Comment non-obvious code** (`feedback_comment_nonobvious_code`): per-family backtest loops, OR-computation, event-window joins all get brief `#` comments.

## Expected mid-execution course corrections

This chapter is large; the chapter-arc pattern guarantees ≥1 surprise per family. Pre-flagged candidates:

1. **Momentum lag-k ρ may be even smaller than Ch7's +0.004 in the Ch11 window.** Ch7 measured over a larger window (251 sessions matches; same data, actually). The headline finding may shift if a re-measure under tighter PIT discipline collapses the +0.004 further. Be ready to reframe §2 around "momentum's signal-to-noise is so small that the cost stack swamps it before optimization can find it." Same shape as Ch4-Ch15 surprises.
2. **ORB confirmation may have a positive cost-aware Sharpe.** ORB is folklore-significant; if the data agrees, this is the chapter's positive headline. The pedagogical risk is over-claiming on a single year of QQQ data — write the verdict so that "positive but CI-straddles-zero" survives a mid-execution upward surprise without sounding triumphalist.
3. **ORB anticipation toxicity may be smaller than Ch13's** (because the strategy is *trying* to be early, not faded). Be ready to reframe §3.5 around "directional bets get a different toxicity profile than reversion bets" — sharper Ch13 pedagogy.
4. **Event-driven with N=8 may produce a "headline" point estimate that's far from zero.** With CI width ±3 Sharpe, a +1.5 point estimate or a −1.5 point estimate are both possible. The chapter should not draw conclusions from N=8 regardless of the point estimate; §4.5 explicitly says so. Exercise 3 (extension to CPI+NFP) becomes the actual test.
5. **§5.3 verdict may genuinely be "none of them survive cleanly."** Pre-state all three outcomes in the spec; pick the actually-true one in execution.
6. **Regime fingerprints in §5.2 may be too noisy to distinguish at N per cell ~10-30.** Reframe as "the right picture but the wrong year of data" — Ch17-18 going-live monitoring continues building the picture.

## Scope hedges (already baked in)

- §4 event-driven is intentionally compressed to one section because N=8 limits what can be claimed. Sample-size honesty doubles as scope hedge.
- §3 breakout has two variants in one section, not two sections.
- §5.2 regime fingerprint heatmap is the synthesis; not repeated per family.
- §5.3 verdict is pre-written for all three outcomes; execution selects the matching narrative.

If chapter still over-runs the ~25-page target during execution, the cleanest cuts are:
- Compress §2.5 / §3.6 regime conditioning per family into §5.2 only (one synthesis section, not three preludes)
- Drop §3 breakout-anticipation variant entirely and run only confirmation; mention anticipation in So-What
- Demote §4 event-driven from "full pipeline" to "single backtest + Exercise 3 carries the rest"

Decisions deferred to execution as the page count signals.
