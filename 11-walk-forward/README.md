# Chapter 11 — Backtesting III: Walk-Forward and Statistical Validation

This is the chapter that closes the deflation arc. Ch8 produced an in-sample Sharpe of **+2.08**. Ch9 fixed the mechanics and brought it to **+0.80**. Ch10 fixed bias from look-ahead and snooping, but every Sharpe Ch10 quoted was still computed on the same data used to choose the strategy's parameters. Ch11 introduces the discipline of separating those two activities — *parameter selection* and *performance estimation*.

The job here is the simplest validation question that exists: **does the strategy survive on data the strategy has never seen?**

Three flavors of "did it work out-of-sample?":

1. **Train/test split** — the cheapest validation. Hold out the last 30% of sessions, fit on the first 70%, evaluate the trained parameter on the held-out portion. Single comparison; quick to compute; honest if you do it once.
2. **Walk-forward optimization** — refit monthly on a 3-month trailing window; concatenate the OOS PnL across all rolls. Yields a continuously-OOS PnL series and a sequence of parameter choices whose stability you can inspect.
3. **Bootstrap CI on OOS PnL** — the OOS Sharpe is itself noisy. The CI is what tells you whether the strategy is statistically distinguishable from random.

The chapter's punchline number — the one to carry into Ch12 and beyond — is the walk-forward concatenated OOS Sharpe with its bootstrap CI. The honest answer for this strategy on this data: **+0.88, 95% CI ≈ (−1.6, +3.5)**. Positive point estimate; CI comfortably includes zero.

## Three things this chapter covers

1. **The IS/OOS gap is the real signal-to-noise.** Section §1. A strategy with IS Sharpe 2.0 and OOS Sharpe 0.6 is real but weak; a strategy with IS Sharpe 2.0 and OOS Sharpe 0.0 was a curve fit. The two look identical at the IS stage; only OOS distinguishes them.
2. **Walk-forward gives you adaptive evaluation.** Section §3. Parameters refit window-by-window; you observe the *sequence* of choices as well as the OOS performance. Parameter stability is its own diagnostic.
3. **A point Sharpe without a CI is incomplete.** Section §4. Even an OOS point Sharpe is a noisy estimator. Block-bootstrapping the OOS PnL — at the trade level *and* at the daily level — gives you both the lower bound (the smallest plausible truth) and the upper bound (the strategy isn't *that* good either).

> **Definition — in-sample (IS).** Performance computed on the exact data used to choose the strategy's parameters. An *upper bound* on what the strategy can really do, never the strategy's actual edge. Always optimistic.
>
> **Definition — out-of-sample (OOS).** Performance computed on data the strategy has never seen — neither during parameter selection nor during any "this looks reasonable" decision. Slightly less optimistic than IS by construction; tracking truth more closely.
>
> **Definition — train/test split.** A single partition of the dataset into a `train` portion (used for parameter selection) and a `test` portion (held out for OOS evaluation). The simplest validation; honest if you only evaluate on the test set *once*.
>
> **Definition — walk-forward optimization.** Repeated train/test splits in chronological sliding-window form. At each step, refit on a trailing window, evaluate on the next window, slide forward. Concatenate OOS evaluations into a single series.
>
> **Definition — deflation factor.** The ratio OOS Sharpe / IS Sharpe. A typical retail strategy deflates to 0.3-0.7. Above 0.7 is suspicious (suggests not enough genuine OOS, or accidental information leakage). At 0 means the IS was noise.

## §1 — The IS/OOS gap is the real signal-to-noise ratio

Every IS Sharpe is, mechanically, an *upper bound* on the strategy's true expected performance. The mechanism is parameter selection: you sweep, you pick the best. The "best" is the maximum over noisy estimates and exceeds any single estimate's mean by construction.

The OOS Sharpe is the lower-variance estimator of truth. Truth itself — what the strategy will actually produce on data not yet observed — sits between IS and OOS in expectation, closer to OOS than to IS.

Two numerical examples to anchor intuition. Both refer to a hypothetical strategy with a "true" Sharpe of 0.5:

- IS = 2.0, OOS = 0.6. Plausible; the IS picks up genuine signal plus some snooping inflation; OOS captures the signal without the inflation. **Real-but-weak**.
- IS = 2.0, OOS = 0.0. Also plausible; the IS was almost entirely noise plus snooping; OOS realized truth = 0. **Curve fit**.

The difference is the deflation factor (OOS / IS):

- 0.30 in the first case (real-but-weak)
- 0.00 in the second (curve fit)

Without OOS, you literally cannot distinguish these two strategies. *Every* serious quant pipeline runs OOS validation; *no* serious quant pipeline reports IS Sharpe as the strategy's edge.

## §2 — Train/test split

The simplest possible validation. We hold out the last 30% of sessions as the test window — 76 sessions, roughly 4 months. We sweep `k_σ` across 21 values on the first 70% (175 sessions), pick the in-sample best, and apply it *unchanged* to the held-out portion.

> **Definition — holdout set.** Synonymous with the test set in a train/test split. The portion of the data the strategy and its parameters are *never* fit to.
>
> **Operational rule:** evaluate on the holdout exactly once. Iterate on the holdout — re-tune after seeing OOS performance — and you have effectively re-merged train and test, with all the snooping that implies.

### Results

| Quantity                          | Value   |
| --------------------------------- | ------- |
| Best train k_σ                    | 1.40    |
| IS Sharpe (train, 175 sessions)   | **+1.65** |
| OOS Sharpe (test, 76 sessions)    | **+0.46** |
| Deflation factor (OOS / IS)       | 0.28    |

**The held-out 30% retained roughly one-quarter of the in-sample Sharpe.** That deflation factor of 0.28 sits at the severe end of the typical 0.3-0.7 range — the strategy was meaningfully fit to the train portion. The OOS Sharpe of +0.46 is below the 0.5 retail-tradable threshold, but only just.

### A subtle finding

Ch10 §4's *full-sample* sweep best was `k_σ = 0.50` with Sharpe +1.86. Here, on the train portion alone, the best is `k_σ = 1.40`. **The "best" parameter is itself unstable across windows.**

That instability is informative. Snooping bias produces unstable choices, not just inflated Sharpes. If the optimizer picks `k_σ = 0.50` on the full sample but `k_σ = 1.40` on the first 70% of sessions, the parameter is not *measuring something stable about the strategy* — it is *fitting noise specific to each window*. Real edges produce stable optimizers.

## §3 — Walk-forward optimization

Train/test split is one comparison. Walk-forward is many — and crucially, it lets the strategy *adapt* between windows. The procedure:

1. Slide a 3-month training window along the data, advancing one month at a time.
2. At each step, refit the strategy parameter (sweep `k_σ` ∈ [0.5, 2.5] in 21 steps; pick IS best) on the trailing 3 months. Refit σ from the same 3 months.
3. Evaluate the refit strategy on the *next* month, using its own σ (point-in-time-clean).
4. Concatenate the OOS trades across all walk-forward steps; compute aggregate metrics on the combined ledger.

The output is a continuously-OOS PnL series and a sequence of parameter choices.

### What the procedure shows

10 effective walk-forward windows after the 3-month warmup. Per-window summary:

| Month   | k_σ best | IS Sharpe | OOS trades | OOS Sharpe |
| ------- | -------- | --------- | ---------- | ---------- |
| 2025-08 | 1.6      | +3.34     |  19        | −0.73      |
| 2025-09 | 1.5      | +5.22     |  42        | +2.49      |
| 2025-10 | 2.5      | +6.47     |  36        | −1.36      |
| 2025-11 | 1.2      | +1.37     | 104        | −0.59      |
| 2025-12 | 0.7      | +1.59     |  77        | +1.36      |
| 2026-01 | 0.7      | +1.35     |  92        | −0.41      |
| 2026-02 | 0.7      | +2.54     | 116        | +5.62      |
| 2026-03 | 1.8      | +4.22     |  64        | +4.53      |
| 2026-04 | 2.1      | +5.36     |   8        | −17.6      |
| 2026-05 | 0.7      | +3.05     |  17        | +2.97      |

**Walk-forward concatenated OOS Sharpe: +0.88** (575 trades over 148 sessions).

### Reading the table

Three observations.

**1. Concatenate the trade ledger; do not average per-month Sharpes.** The 10 monthly Sharpes range from −17.6 (Apr) to +5.6 (Feb); their simple mean is dominated by the two anomalously bad windows. What the strategy would have *produced* in real trading is the trade-weighted concat number (+0.88), where 116 February trades count more than 8 April trades.

The April number deserves a flag. The optimizer picked `k_σ = 2.1` on March's training window, which is restrictive; only 8 trades fired on the OOS month; one or two big losses dominate the Sharpe. **Small monthly samples produce noisy monthly Sharpes** — another reason not to equally-weight per-month aggregates.

**2. Walk-forward (+0.88) > train/test (+0.46) on this data.** Counter-intuitive at first — the more elaborate procedure looks better. The reason is regime adaptation: the per-month refit picks up on volatility shifts that the single-fixed-parameter train/test split cannot. When the market regime in late 2025 shifts (closing-minute volatility increases), walk-forward raises `k_σ` mid-stream; train/test cannot.

That said, walk-forward's adaptiveness *also* gives the optimizer 10 chances to fit noise instead of one. Per-window snooping is a real bias — see §5. The +0.88 number is the OOS aggregate of 10 per-window IS-best choices, not the OOS performance of a single fixed parameter; it inherits some optimization variance.

**3. Parameter stability is poor.** The selected `k_σ` ranges from 0.7 to 2.5 across the 10 windows — a 3.5× swing. The mode is 0.7 (4 of 10 windows). Standard deviation across windows is 0.66.

A stable strategy should produce a stable optimizer. If `k_σ` is genuinely the right knob to tune, repeated refits should pick similar values — perhaps drifting slowly with regime, but not jumping by a factor of 3 between months. Here it jumps. **The in-sample best is mostly noise.**

## §4 — Bootstrap CI on the walk-forward OOS ledger

The point Sharpe of +0.88 is one number. The CI is the actual evidence. Two bootstrap variants:

1. **Trade-ledger bootstrap** — resample the 575 OOS trades (or sample contiguous blocks).
2. **Daily-PnL bootstrap** — aggregate trades to daily PnL (sum of per-trade PnL within each session); resample the daily series.

The two answer different questions. Trade-level CI captures per-trade noise; daily-level CI captures regime persistence. Ch9 §5 predicted that block size will start to matter at the daily level even though it didn't matter at the per-trade level — this chapter confirms that prediction.

### Results

| Unit         | Block size | 95% CI               | Width |
| ------------ | ---------- | -------------------- | ----- |
| trade-ledger | 1          | (−1.61, +3.47)       | 5.08  |
| trade-ledger | 5          | (−1.76, +3.44)       | 5.20  |
| trade-ledger | 20         | (−2.10, +3.75)       | 5.85  |
| daily-PnL    | 1          | (−1.56, +3.66)       | 5.22  |
| daily-PnL    | 5          | (−1.81, +3.66)       | 5.47  |
| **daily-PnL** | **20**    | **(−0.79, +3.70)**   | **4.49** |

**All CIs comfortably straddle zero.** The point estimate (+0.88) sits inside an interval of roughly (−1.6, +3.5). Translation: even the *positive* point estimate cannot be statistically distinguished from random on a single year of OOS data.

Compare the two bottom rows of each unit. On the **daily-PnL** ledger, block=20 *narrows* the CI (5.22 → 4.49) — block bootstrapping captures regime persistence, and the wider blocks correctly account for the fact that consecutive days are correlated through shared market regime. On the **trade ledger**, block=20 *widens* the CI (5.08 → 5.85) — because per-window blocks of 20 trades sometimes pull whole "Feb" or "Apr" runs together, and those windows are themselves more variable than independent trades.

Two aggregation levels, two different stories. The daily-level result is the more pedagogically interesting one: it demonstrates that block-bootstrap calibration matters when you aggregate to a unit where serial correlation actually exists. The Ch9 §5 forward pointer is paid in full.

The honest decision-rule:

> A point Sharpe without a CI is incomplete. A 95% CI on annualized Sharpe that straddles zero on a 1-year OOS window means the strategy is *not yet shown* to have edge — even if the point estimate is positive. Either find more data (multi-year history) or accept that the strategy is statistically indistinguishable from chance on the data you have.

## §5 — Multiple comparisons across walk-forward refits

A subtle issue worth naming. Each walk-forward refit selects from a 21-point parameter grid. Across 10 windows, the implicit test count is 10 × 21 = 210 in-sample comparisons. Bonferroni's bar at α / 210 ≈ 0.00024 corresponds to a critical |t| of 3.69 — even higher than Ch10 §4's 3.04 for a single 21-point sweep.

In practice the OOS-aggregate Sharpe's bootstrap CI handles this implicitly: the CI is wide because the realized OOS performance is itself noisy, and that noise *includes* per-window fitting variance. We don't need an explicit Bonferroni adjustment on top — the CI lower bound is already negative.

For readers who want the formal version: the analogous procedure here is *forward-validation Bonferroni* — adjust the OOS critical t for the implicit number of comparisons across all walk-forward windows. The conclusion on this data is unchanged because the OOS CI is so wide already.

The cleaner mental model: **walk-forward replaces in-sample bias with out-of-sample variance.** You no longer pretend you knew the parameters in advance; you accept that each window's optimizer makes a noisy choice; the aggregate noise shows up as a wide OOS CI. Both bias and variance contribute to "we don't know if this strategy works"; walk-forward shifts which one carries the load.

## §6 — Pass / fail on walk-forward criteria

Three criteria for "the strategy survived walk-forward":

1. **OOS Sharpe ≥ 0.5** (a minimum threshold for a tradable retail strategy, *ignoring* costs — costs come in Ch12).
2. **OOS Sharpe 95% CI lower bound > 0** (statistically distinguishable from no edge).
3. **Parameter stable across walk-forward windows** (the in-sample-best is not a moving target).

This strategy on this data:

| Criterion                                        | Value                               | Verdict     |
| ------------------------------------------------ | ----------------------------------- | ----------- |
| Train/test OOS Sharpe ≥ 0.5                       | +0.46                               | borderline  |
| Walk-forward concat OOS Sharpe ≥ 0.5              | +0.88                               | passes      |
| Walk-forward OOS CI lower bound > 0               | trade-ledger b=1: (−1.61, +3.47)    | **FAILS**   |
| Parameter stable across walk-forward              | k_σ ∈ (0.7, 2.5); std = 0.66        | **FAILS**   |

**Verdict: the strategy fails 2 of 4 sub-criteria.**

The walk-forward concat Sharpe of +0.88 looks tradable in isolation, but the bootstrap CI says we cannot yet distinguish it from random, and the parameter swings across windows say the in-sample-best is not stable enough to deploy. Translation: **don't trade this.**

That conclusion is honest, not despairing. The strategy showed some structure (the closing-window mean-reversion mechanism Ch7 identified is real), survived honest mechanics (Ch9), survived bias correction (Ch10), and the walk-forward OOS Sharpe is positive — but didn't clear the statistical-significance bar on a single year of data. The natural follow-ups: more data (multi-year history would tighten the CI substantially), better cost modeling (Ch12 — likely pushes this across zero anyway), and exploring the rest of the strategy taxonomy (Ch7's other three families: momentum, breakout, event-driven).

This is what an honest pipeline produces. **Most candidate strategies fail walk-forward; that's the whole point of running it.**

## §7 — Closing the deflation arc

Across Ch8 → Ch11 we have watched a single strategy's headline Sharpe shrink under each layer of honest evaluation:

| Stage                                       | Sharpe   | What changed                                |
| ------------------------------------------- | -------- | ------------------------------------------- |
| Ch8 vectorized backtest                     | +2.082   | Inflated by overlap + same-bar bug           |
| Ch9 event-driven, next-open                 | +0.803   | Honest mechanics; CI already straddles 0     |
| Ch10 trailing-σ baseline (still in-sample)  | +1.641   | Bias-corrected threshold; bias was data-dependent |
| Ch10 sweep best (in-sample, snooped)        | +1.859   | Cherry-picked from 21 thresholds             |
| Ch11 train/test (best-train-k OOS)          | +0.460   | Held-out 30%; deflation factor 0.28          |
| **Ch11 walk-forward (concatenated OOS)**    | **+0.883** | **Continuous OOS over 10 monthly refits**    |

The end-to-end deflation: **+2.08 → +0.88, a 58% loss of headline Sharpe before costs**. The honest number for "what does this strategy give us, decision-ready" is the bottom row: **walk-forward concat OOS Sharpe of +0.88, with 95% CI of approximately (−1.6, +3.5)**.

The headline +2.08 from Ch8 was real in the sense that it was *measured* on the data. It was wrong in every other sense.

> Always ask for the walk-forward number with a CI. If it's missing, the strategy hasn't been validated.

## So what?

Decision rules this chapter unlocks:

1. **Quote walk-forward OOS Sharpe with a bootstrap CI as the strategy's edge — never the in-sample number.** If the lower bound of the 95% CI is below zero, the strategy isn't yet a strategy; it's a hypothesis. More data or a better strategy idea is the answer; deploying-and-hoping is not.
2. **Treat the deflation factor (OOS / IS) as the strategy's signal-to-noise.** A factor below 0.3 means most of the in-sample edge was fit; above 0.7 means either the strategy is unusually robust or you have accidental leakage. Investigate either way.
3. **Watch parameter stability.** A walk-forward in which the optimizer keeps picking a different parameter window-after-window is fitting noise. A real edge should produce a stable optimizer (perhaps drifting slowly with regime, but not jumping 3×).
4. **Concatenate the trade ledger across walk-forward windows; weight by trade count.** Equal-weighted monthly Sharpes give an arithmetic-mean statistic that is *not* what the strategy realizes. Trade-weighted concat is realized-PnL-style and properly handles small months.
5. **Block-bootstrap when aggregating to PnL series.** On per-trade ledgers, block size barely changes width. On daily PnL, block size matters because regimes persist. Different unit of analysis, different bootstrap structure.

What this chapter cannot yet tell you:

- **Whether the strategy survives realistic costs.** Ch12 stacks bid/ask spread, commission, and slippage on the walk-forward OOS strategy. Per-trade std on the OOS ledger is ~7.4 bp; per-trade mean is ~0.16 bp. A 1 bp cost is 6× the per-trade mean. Ch12 will quantify which (if any) thresholds survive.
- **Whether the strategy works on multiple instruments.** Exercise 2 below transfers the pipeline to SPY; the chapter doesn't itself.
- **Whether a different strategy family does better on the same machinery.** Ch7's other three families (momentum, breakout, event-driven) get instances in Ch16, evaluated through this same Ch9-12 discipline.

## Key Terms

| Term                       | Definition                                                                                                       |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| In-sample (IS)             | Performance on the data used to choose strategy parameters. Always an upper bound on truth.                       |
| Out-of-sample (OOS)        | Performance on data the strategy has never seen. Lower-variance estimator of truth.                              |
| Train/test split           | Single partition of the data into a fit portion (train) and a held-out portion (test).                          |
| Holdout set                | Synonymous with test set. Operational rule: evaluate exactly once.                                              |
| Walk-forward optimization  | Repeated train/test splits in chronological sliding-window form. Refit, evaluate, slide; concatenate OOS.       |
| Deflation factor           | Ratio OOS Sharpe / IS Sharpe. Typical retail strategies deflate to 0.3-0.7.                                       |
| Parameter stability        | Whether the in-sample-best parameter is similar across walk-forward windows. Stability ⇒ real edge.              |
| Block bootstrap (on PnL)   | Resampling contiguous blocks of length *b* — preserves serial correlation. Matters on daily PnL more than on per-trade ledgers. |
| Forward-validation Bonferroni | Multiple-comparison correction applied across walk-forward refits. Implicit in the OOS CI on this data.       |

## Up next

**Ch12 — Costs, slippage, and capacity.** Ch11's +0.88 walk-forward OOS Sharpe is a zero-cost number. Ch12 stacks realistic frictions: bid/ask spread, commission per trade, slippage as a function of trade size and book depth. Per-trade mean PnL on this strategy is ~0.16 bp; even a 1 bp round-trip cost flips expectancy across zero. Ch12 will quantify the cost the strategy can absorb before it dies — and what kind of edge would be needed to survive realistic execution.

After Ch12, Part 8 (Ch14-16) revisits sizing, regime detection, and additional strategy families — each evaluated through the same Ch9-12 discipline this chapter culminates.

## Exercises

1. **Weekly walk-forward refits.** §3 used monthly windows (~10 OOS rolls). Re-run with a weekly window (1-week training, 1-week OOS, ~50 rolls) on the same data. Does the OOS Sharpe move? Does the CI tighten — you have more rolls, but each is shorter and noisier? *Hint:* the trade-off is between bias (slower refit lags regime shifts) and variance (faster refit fits noise). Plot the parameter-stability chart for the weekly version and compare.
2. **SPY transfer.** Repeat the entire walk-forward pipeline on SPY 1-min (path: `../06-bridge-to-intraday/data/spy_1min.parquet`). Same N=1, K=3, same closing-window gate. Does the conclusion match QQQ's? If different, what about SPY's price dynamics could explain the difference? *Hint:* SPY's underlying volatility is lower than QQQ's, so per-trade signal-to-noise may be smaller; but spread and commission costs are similar in absolute basis points, which could matter relatively more for SPY.
3. **Two-parameter walk-forward.** §3 only refit `k_σ`; `N` was fixed at 1. Add `N` to the walk-forward sweep — `N ∈ {1, 2, 3, 5}` × `k_σ` in 21 steps = 84 implicit tests per window. Does the OOS Sharpe go up, down, or sideways? What about parameter stability — is N stable while k_σ swings, or do both move? *Hint:* adding more freedom for the optimizer usually inflates IS Sharpe; OOS is the test of whether the freedom was used or wasted.
