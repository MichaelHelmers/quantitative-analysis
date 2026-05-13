# Chapter 15 Design — Intraday Vol & Regime Detection

**Date:** 2026-05-13
**Status:** Approved (Part 8 middle chapter — vol/regime measurement track).
**Spine:** Ch14 left σ̂_t as a flat-rolling-window placeholder in its volatility-targeting formula. Ch15 builds the real σ̂_t — decomposed into within-session seasonality, across-session GARCH persistence, and across-regime structural shifts — and feeds it back into Ch11's strategy ledger as a concrete sizing/filtering experiment. This is also the chapter that absorbs the retired Ch9 GARCH salvage.

## Why this chapter exists

Three open σ-related promises converge here:

1. **Ch14 §4** wants a non-naive σ̂_t for vol targeting. A 20-day rolling std ignores intraday seasonality (vol at the open is 3-5× midday) and ignores autocorrelation in vol (today's σ predicts tomorrow's via GARCH).
2. **Ch7 §7** named three drivers of edge decay; *regime change* was one. Ch15 builds the detectors that flag regime shifts in real time.
3. **Pivot 2026-05-07** committed to the GARCH salvage from retired Ch9. The hand-rolled MLE pedagogy is a chapter highlight worth preserving.

The chapter answers three questions about σ at three time-scales:

- **Within-session.** Where in the session am I? Vol at minute-of-session m.
- **Across-session.** What kind of week is this? σ̂(day_t) from GARCH.
- **Across-regime.** Is the world structurally different from last month? Four regime detectors compared side-by-side.

Then it cashes everything: apply σ̂_t vol targeting and high-vol-regime filtering to Ch11's walk-forward MR ledger, measure the PnL/Sharpe/DD impact.

## Three-flavor framing

1. **Within-session.** σ depends on minute-of-session m; the intraday U-shape from Ch6 formalized into a per-minute estimator σ̂_seasonal(m).
2. **Across-session.** σ depends on the recent vol history; EWMA → GARCH(1,1) gives σ̂_GARCH(day).
3. **Across-regime.** σ depends on which regime is active; four detectors flag regime transitions.

The three flavors compose: σ̂_t = σ̂_GARCH(day_t) × σ̂_seasonal(m_t) / mean(σ̂_seasonal). Regime detectors sit on top as filters / state indicators.

## Section structure

### §1 — Setup: σ̂_t plug-in

Recap Ch14's vol-target formula and its σ̂_t placeholder. State the three time-scales. Recap Ch6 U-shape and retired Ch9 GARCH headlines briefly so the reader knows where the pieces come from. Define "regime" inline (a stretch of time where the data-generating process's parameters are stable; a regime change is a parameter shift) — `feedback_define_every_term`.

Up-front foot-gun callout: σ has three temporal axes and conflating them is the canonical mistake. A 20-day rolling std on 1-min bars over-weights opening-burst minutes if the rolling window happens to span the open; a daily-vol GARCH model applied to intraday minutes ignores seasonality entirely.

### §2 — Within-session vol seasonality

Rebuild Ch6's U-shape as a calibrated estimator, not just a plot.

**Data.** Ch6 QQQ 1-min parquet, Ch11 window (251 RTH sessions, 95,318 bars).

**Estimator.** For each minute-of-session m ∈ {0, 1, ..., 389}, compute σ̂_seasonal(m) = std of 1-min log returns at minute m across all sessions in a rolling training window (e.g., trailing 60 sessions; honors Ch10's point-in-time discipline).

**Headline plot.** σ̂_seasonal(m) vs m for QQQ Ch11 window. Peak-to-trough ratio is the headline number (expected 3-5×).

**Where-clauses on every formula** (`feedback_define_formula_symbols`). Define m, log return, std-across-sessions explicitly.

**Sanity.** Compare to Ch6 §4's U-shape — should match shape, with the chapter window cropped tighter.

### §3 — Across-session: EWMA → GARCH(1,1)

**EWMA primer.** Closed-form recursion σ̂²_t = (1−λ) r²_{t−1} + λ σ̂²_{t−1}. RiskMetrics λ = 0.94. Foot-gun: no long-run mean, so σ̂ has no anchor — if r runs hot for a long stretch, σ̂ drifts up without bound (in expectation).

**Coin-flip MLE warm-up.** N=17 flips, 7 heads → MLE p̂ = 7/17 = 0.412. Two-line derivation: log-likelihood = k log p + (N−k) log(1−p); set ∂/∂p = 0. Why this matters: GARCH is the same procedure applied to a richer likelihood. Reuses retired Ch9's pedagogy verbatim.

**GARCH(1,1).** Definition: σ²_t = ω + α r²_{t−1} + β σ²_{t−1}, with r_t = σ_t · z_t, z_t i.i.d. N(0,1). Where-clauses on ω, α, β, persistence (α+β), long-run variance ω/(1−α−β).

**MLE implementation.** Hand-rolled via `scipy.optimize.minimize`. Negative log-likelihood with parameter constraints (ω > 0, α ≥ 0, β ≥ 0, α + β < 1). Initialization at ω = 0.02·var(r), α = 0.1, β = 0.85.

**Fit on QQQ session-bar returns** (where session-bar return = close-to-close log return on RTH session). Report ω̂, α̂, β̂, persistence, long-run σ̄ annualized. Expected: persistence ~0.97 paralleling retired Ch9's SPY result.

**Diagnostic.** ACF of standardized residuals z_t = r_t / σ̂_t (should be flat — GARCH absorbed the autocorrelation in squared returns) and ACF of raw squared returns (should be strongly positive — the structure GARCH was fitted to absorb). Side-by-side plot.

**GARCH-VaR table.** Realized σ̂_t on the FOMC days within Ch11 window vs σ̂_t on non-event sessions. Quote the ratio.

### §4 — Combining within- and across-session

The multiplicative decomposition:

σ̂_t = σ̂_GARCH(day_t) × σ̂_seasonal(minute_of_session_t) / mean_m(σ̂_seasonal(m))

The mean-normalization in the denominator keeps σ̂_GARCH interpretable as "average-minute" volatility. Without it, the σ̂_t units would be scaled by the choice of m.

**Sanity plot.** Pick one representative high-vol session (e.g., a FOMC day in Ch11 window) and one low-vol session. Overlay σ̂_t against realized 1-min |r_t| RMS. The combined estimator should track both the within-session U-shape and the day-level vol regime.

**Forward-pointer to §6.** This σ̂_t is the input that Ch14 §4 vol-targeting needs.

### §5 — Regime detection: four methods compared

The chapter's research section. Four methods, applied to the same Ch11 window so they can be compared directly.

#### §5.1 — Vol-threshold

Define high-vol regime as σ̂_GARCH(day_t) > p80 of its trailing-1-year distribution. The simplest possible regime indicator. Plot a stacked indicator timeline across Ch11 window: which days are flagged?

Where-clauses on the threshold choice (p80 is conventional; tested at p70 / p80 / p90 in Exercise 4).

#### §5.2 — Event-window

Calendar-based regime: tag sessions overlapping with FOMC announcements, CPI releases, NFP releases. Calendar already in Ch6 (FOMC) — extend to CPI and NFP via BLS-published schedule. Cache as a small CSV in the chapter's data/ folder.

Plot the tagged sessions alongside §5.1's threshold flags. Confusion-style overlap: of the §5.1-flagged days, how many are also event-tagged?

#### §5.3 — Markov-switching 2-state HMM

Latent state s_t ∈ {low-vol, high-vol}. Observation: session-bar return r_t. Model: r_t | s_t = i ~ N(0, σ²_i), with transition matrix P[s_t = j | s_{t−1} = i] = π_{ij}. Six parameters: σ²_0, σ²_1, π_{00}, π_{11} (the other two follow), plus initial state distribution.

**Estimation.** EM algorithm:
- E-step: forward-backward gives γ_t(i) = P[s_t = i | data]
- M-step: re-estimate σ²_i and π_{ij} from γ

If `hmmlearn` works under current pandas, use it (with a sanity-check that the parameter estimates match a hand-rolled implementation on a small sample). If broken, fall back to hand-rolled EM — same precedent as retired Ch9's `arch` fallback, and the pedagogical win is the same.

**Headline plot.** Smoothed P[s_t = high-vol | data] across Ch11 window, with realized 20-day rolling vol overlaid.

**What it adds over §5.1.** §5.1 is a deterministic threshold on a single σ-statistic; §5.3 is a probabilistic state assignment that integrates the full sequence. Highlight cases where they disagree.

#### §5.4 — CUSUM change-point detection

Cumulative-sum statistic on standardized residuals z_t² − 1 (which is mean-zero under correctly-specified GARCH). When the running sum drifts past a threshold, declare a change-point. Mark detected change-points on Ch11 window.

**Bayesian online change-point detection named-only.** One paragraph + reference to BOCPD if the reader wants more. Scope hedge per spec discussion.

#### §5.5 — Side-by-side comparison

Overlay all four regime indicators on a single timeline. Which method fires when? Where do they agree? Where do they disagree? Narrative interpretation — no formal confusion matrix because the regimes are latent and there's no ground truth.

### §6 — Apply to Ch11 ledger

The chapter's payoff. Two experiments using Ch11's walk-forward OOS trade ledger (575 trades, 148 sessions, Sharpe +0.88 pre-cost).

**Experiment 1 — Vol targeting.** Re-size each trade by k_t = target_daily_vol / σ̂_t, where σ̂_t is the §4 combined estimator at trade entry minute and target_daily_vol = 1%. Report:
- Unit-notional ledger Sharpe / max DD (baseline = Ch11 number)
- Vol-targeted ledger Sharpe / max DD
- Realized average leverage and leverage range

Honors Ch14 §4 forward-pointer.

**Experiment 2 — High-vol filter.** Drop trades tagged by §5.1 vol-threshold (use only the most-conservative regime method to keep the experiment clean; HMM filter explored in Exercise 3). Report:
- Filtered trade count vs total
- Filtered ledger Sharpe / max DD vs unfiltered
- Subset analysis: PnL of the *removed* trades — is the filter dropping winners or losers?

Honors Ch7 §7 regime-decay forward-pointer.

**Expected headline.** Vol targeting smooths PnL; the realized Sharpe may shift slightly in either direction (vol targeting doesn't change expected return, only its volatility, but it does change *which* trades get amplified, which interacts with serial correlation). High-vol filter is harder to call — depends on whether MR works better or worse in high-vol regimes on this window.

### §7 — So what + Key Terms + Up next

**So what?** Three decision rules:
1. Always decompose σ̂_t into seasonality × persistence before vol-targeting. Flat rolling estimators are a known foot-gun on intraday data.
2. Pick *one* regime indicator that maps to your strategy's failure mode and commit to it. Combining indicators sounds appealing but introduces a multiple-comparison snooping risk (Ch10).
3. Vol targeting changes the shape of the PnL distribution, not its mean. Use it when max-DD matters more than mean return (Ch14 §5 trade-off).

**What this chapter can't yet tell you:** which regime indicator is *right*. Regimes are latent. The best practice is to build a small basket of indicators, use them as inputs to position sizing rather than binary on/off filters, and accept that any single indicator will sometimes be wrong.

**Key Terms (target 10).** Volatility seasonality, EWMA, GARCH(1,1), persistence, long-run variance, standardized residual, regime, hidden Markov model, EM algorithm, CUSUM change-point.

**Up next.** Ch16 hunts for real positive-EV strategies beyond Ch8's MR; Ch15's regime tools become the "when does each family work?" framework for Ch16's family comparison.

## Data

Reuses Ch6 QQQ 1-min parquet (251 RTH sessions, 95,318 bars, 2025-05-08 → 2026-05-07).
Reuses Ch11 walk-forward OOS trade ledger (read-only).
New small data file: CPI and NFP release calendar 2024-2026 cached as `15-intraday-vol-regime/data/event_calendar.csv` (~3 dozen rows). FOMC dates from Ch6 reused.

## Dependencies

- `numpy`, `scipy.optimize`, `scipy.stats` (already installed)
- `pandas`, `matplotlib` (already installed)
- `hmmlearn` — *new*, with hand-rolled EM fallback if broken under pandas 3.0 (same risk-mitigation pattern as retired Ch9's `arch` fallback)

## Exercises

1. **SPY transfer.** Re-run §2 seasonality and §3 GARCH on SPY. Compare U-shape ratio and GARCH persistence; report which time-scale shows more SPY/QQQ divergence.
2. **EWMA λ sensitivity.** Forecast σ̂_t with λ ∈ {0.90, 0.94, 0.97} on QQQ session bars. Compare 1-step forecast MSE on a holdout. Which λ wins and by how much?
3. **HMM vs vol-threshold filter.** Re-run §6 Experiment 2 using the §5.3 HMM high-vol state instead of §5.1 vol-threshold. Compare filtered ledger Sharpe / max DD.
4. **Vol-targeting at different targets.** Re-run §6 Experiment 1 at target_daily_vol ∈ {0.5%, 1.0%, 1.5%, 2.0%}. Plot (max DD vs target_vol) and (Sharpe vs target_vol). Find the empirical sweet spot.

Worked solutions for Exercises 2 and 4 in the lesson notebook; 1 and 3 stay as prompts only.

## Promises honored

- **Ch14 §8** "Ch15 refines σ̂_t" — paid in §2-§4 (decomposition) and §6 Experiment 1 (applied to Ch11 ledger).
- **Ch7 §7** edge-decay regime-change driver — paid in §5 (detectors) and §6 Experiment 2 (filter applied).
- **Ch7 §promise** "Ch15 revisits §6 conditioning at higher resolution" — paid: §2 builds a per-minute seasonality estimator beyond Ch7's coarse opening/midday/closing buckets.
- **Pivot 2026-05-07** GARCH salvage — paid in §3 (EWMA, GARCH(1,1), hand-rolled MLE).
- **Ch2** vol clustering forward-pointer — paid: §3 GARCH is the canonical model of the clustering Ch2 documented.
- **Ch6** intraday U-shape — formalized in §2.
- **Ch10** point-in-time discipline — §2 uses trailing-window estimator, not whole-sample; §5 detectors use only past data.

## Promises to honor in later chapters

- **Ch16** uses §5 regime indicators as conditioning variables for "when does each strategy family work?" Each family (momentum, breakout, event-driven) is expected to have a different regime fingerprint.
- **Ch17-18** going-live execution: σ̂_t feeds real-time risk monitoring; HMM smoothed state probabilities become a live signal.
- **Ch14 §4** placeholder σ̂_t — fully replaced by §4 combined estimator going forward.

## Pedagogical notes

- **Concept before statistics** (`feedback_concept_before_statistics`): name the three time-scales in §1 before any formula; recap §7 by time-scale, not by tool.
- **Define every term on first use** (`feedback_define_every_term`): "regime," "latent state," "EM," "EWMA," "persistence," "long-run variance," "change-point" all get inline glosses + Key Terms entries.
- **Define every formula's symbols** (`feedback_define_formula_symbols`): EWMA recursion, GARCH equation, multiplicative decomposition, HMM transition matrix, CUSUM statistic — all carry where-clauses.
- **Push interpretations past description** (`feedback_push_interpretations_past_description`): every regime plot gets a "what this means for the next position you take" paragraph naming concrete windows in Ch11 (e.g., the FOMC day where vol-threshold and HMM disagree).
- **No external knowledge leaps** (`feedback_no_external_knowledge_leaps`): "Markov chain," "forward-backward," "CUSUM" need inline definitions. CPI / NFP get scale and release-mechanics glosses before being used as regime tags.
- **Comment non-obvious code** (`feedback_comment_nonobvious_code`): GARCH MLE objective, HMM EM loop, CUSUM running statistic all get brief `#` comments.

## Expected mid-execution course corrections

Continuing the chapter-arc pattern (every chapter Ch4-Ch13 had at least one). Likely candidates:

1. **GARCH persistence on a 1-year QQQ window.** Retired Ch9 quoted persistence 0.976 on 20-year SPY. On a 1-year QQQ window with N≈250 session bars, the estimate is noisy and may come out 0.90-0.99 with a wide CI. Be ready to reframe §3 around "what 250-obs GARCH tells us vs 5000-obs GARCH" — paying off Ch4 sample-size lessons.
2. **Seasonality estimator with point-in-time discipline.** A trailing-60-session per-minute estimator with only 60 observations per minute has substantial sampling noise. The U-shape may look ragged. Be ready to reframe §2 around the bias-variance trade-off in window length (Exercise 3 of Ch10 territory).
3. **HMM may not separate two states cleanly.** EM may converge to a degenerate solution where both states have similar σ. If so, reframe §5.3 around "the data doesn't strongly support two regimes on this window" — itself a useful pedagogical lesson about latent-variable model fragility.
4. **Vol-targeting Sharpe on Ch11 ledger may move very little.** If MR returns are roughly uncorrelated with σ̂_t at trade entry, vol targeting is roughly a constant rescaling. Be ready to reframe §6 Experiment 1 around "vol targeting reshaped *which* trades dominate but not the mean."
5. **High-vol filter may drop the strategy's best trades.** MR often works *better* in high-vol regimes (more overshoots to fade). If §5.1 filter drops the winners, Experiment 2 produces a *negative* result — pedagogically rich, matches the chapter-arc pattern of "the intuitive bet was wrong."
6. **`hmmlearn` may be broken.** Fallback to hand-rolled 2-state EM. Document the install issue in §1 implementation note. The fallback is meaty (~30 lines of NumPy) but tractable.

## Scope hedges (already baked in)

- §5.4 Bayesian online change-point — named-only, not worked.
- HMM is 2-state, not k-state.
- §5 confusion matrix is narrative, not formal.
- §6 Experiment 2 uses only §5.1 vol-threshold; HMM filter is Exercise 3.

If the chapter still over-runs (target ~18-22 pages), the cleanest cut is to demote §5.4 CUSUM to a half-page named-only treatment alongside Bayesian, and let §5.1 / §5.2 / §5.3 carry the regime-detection narrative. Decision deferred to mid-execution if the page count signals trouble.
