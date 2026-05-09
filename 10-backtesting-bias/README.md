# Chapter 10 — Backtesting II: Bias and Data Integrity

Chapter 9 fixed the *mechanics* of the backtest. The headline Sharpe — about +0.80 on the canonical `next_open` ledger — is now an honest answer to "what would this strategy have produced if you'd run it bar-by-bar with point-in-time fills?" That is a separate question from "is +0.80 a real edge or a fitted artifact?" Mechanics being right doesn't tell you whether the strategy is **statistically distinguishable** from random.

This chapter separates those questions. We will hit Ch9's strategy with three classic biases:

1. **Look-ahead bias** — using future information to make past decisions.
2. **Survivorship bias** — backtesting on a universe that excludes failed entities.
3. **Snooping / multiple comparisons** — picking the best parameter on in-sample data and quoting that parameter's in-sample performance as the strategy's edge.

Look-ahead and snooping get worked examples. Survivorship is named-only — QQQ-as-ETF is essentially immune, and a full treatment requires delisted-ticker price data we don't have.

The pedagogical thread tying them together:

> Ch7 §7 distinguished "edge that decayed" (was real, now isn't) from "edge that was never there" (looked real because of a bias). **This chapter is about the second category.** Ch9 measured a Sharpe; Ch10 asks whether the measurement was honest. Ch11 will ask whether the answer survives out-of-sample.

## Three things this chapter covers

1. **Look-ahead bias on the entry threshold.** The σ used to set the entry threshold should be computable from data available at the time of the trade. Ch9 used the whole-sample σ — an honest mistake we now correct with a trailing-20-session σ. The chapter's first surprise: the "bias" doesn't always go in the direction you expect.
2. **Survivorship bias** — named only. We sketch the mechanism, quote the empirical magnitude (1-2% annualized Sharpe inflation on US equity universes per published research), explain why our QQQ-based strategy is essentially immune, and point at where to get delisted-ticker data if your strategy ever needs it.
3. **Parameter snooping with Bonferroni and Holm corrections.** Sweep `k_σ` across 21 values. Pick the best in-sample Sharpe. Apply multiple-comparison correction to the best parameter's t-statistic. The result is the cleanest possible "your in-sample Sharpe doesn't mean what you think" demonstration.

> **Definition — bias.** In the backtesting context: any structural feature of how the simulation is conducted that shifts measured performance away from what an actually-deployed strategy would have produced. Bias is *not* model error or "the strategy doesn't work." Bias is *the simulation lies, and the strategy might or might not work.*
>
> **Definition — point-in-time threshold.** A threshold (here, 1.0σ for the entry rule) where σ is computable from data observable strictly before the moment of decision. Whole-sample σ is *not* point-in-time; trailing σ over the previous *L* sessions is.

## §1 — Edge that decayed vs edge that was never there

Ch7 §7 named three drivers of edge decay: crowding, regime change, and parameter drift. All three describe edges that *were* real and *became* less real. This chapter is about a different failure mode — edges that *looked* real because the measurement was wrong.

The two failure modes look identical in a backtest report. Both produce a degraded-or-zero forward Sharpe relative to the in-sample number. The difference is causal:

- **Decayed edge** — there was a mechanism; capital arrived and ate it; or the regime changed and the mechanism stopped firing.
- **Never-there edge** — there was no mechanism; the in-sample Sharpe was an artifact of look-ahead, snooping, or a curve fit.

Telling them apart matters because they suggest different responses. A decayed edge might come back; a curve fit will not. The diagnostic tools are different too: walk-forward (Ch11) catches both, but a *parameter-stability* analysis specifically targets curve fits.

This chapter focuses on detection — how to spot the never-there variety before deploying a strategy that depends on it.

## §2 — Look-ahead bias: a worked bug

The strategy we inherit from Ch9 uses an entry threshold of `1.0 × σ(prior_N)`, where σ was computed across **the whole sample** of closing-window prior_N values — all 251 sessions of QQQ 1-min data. That σ averages return scatter across regimes the strategy hadn't lived through yet. A trader running this strategy on day 1 of the backtest could not have known what σ was going to be — they would have computed it from whatever history they had at the moment.

The point-in-time-correct version: at the start of each session, compute σ from the **prior 20 sessions** only. The lookback window slides forward; we only ever use information that was actually available.

> **Definition — look-ahead bias.** A specific class of bias in which a quantity used in a backtest decision was computed using information that wasn't observable at the time of the decision. Whole-sample statistics (means, standard deviations, quantiles) are the textbook example; less obvious examples include "data-cleaning" steps that look across the full history, fitted parameters refit each day on data that includes today, or features computed at one bar resolution and joined back at another.
>
> *Where:*
> - "decision" — any operation that fires only when a condition is met (entry threshold, stop-loss level, position sizing rule).
> - "wasn't observable" — strictly, the computation depends on at least one observation indexed at time ≥ *t*. A future close, a future return, a future regime label — all disqualify.
>
> The fix: every feature in the decision logic must be derivable from the panel restricted to `t' < t`. The cleanest way to enforce this is procedural — an event-driven loop that mechanically only "knows" about the past.

### What the experiment shows

Two backtests, same strategy, same data:

| σ source                         | Trades | Annualized Sharpe | t-stat | Expectancy (R) |
| -------------------------------- | ------ | ----------------- | ------ | -------------- |
| `whole_sigma` (look-ahead)       | 900    | **+0.82**         | +0.78  | +0.038         |
| `trailing_sigma` (point-in-time) | 868    | **+1.64**         | +1.52  | +0.075         |

The point-in-time-correct version produces a *higher* in-sample Sharpe than the look-ahead version. **The look-ahead bias did not inflate Sharpe in this experiment. It deflated it.**

Why? The trailing σ is *adaptive*. When recent volatility is low, the threshold drops and the strategy fires on smaller overshoots. When recent volatility spikes, the threshold rises and the strategy stays out. The whole-sample σ averages across all regimes — including ones the strategy had not yet encountered — so it under-fires in the calm regimes (when overshoots that look small relative to whole-sample σ are actually large relative to recent σ) and over-fires in the wild regimes (when overshoots that look large relative to whole-sample σ are actually small relative to recent σ).

The pedagogical lesson is sharper than "look-ahead inflates Sharpe":

> Look-ahead bias can move Sharpe in *either* direction. The bug is not the inflation direction — the bug is that you used information you didn't have. The fix is non-negotiable, regardless of which way the Sharpe shifts.

A reader who only knew the textbook framing — "look-ahead inflates" — would, if they happened to find a trailing-σ Sharpe lower than whole-sample-σ Sharpe, conclude the bias-correction worked and quote the lower number. They would be wrong about the *direction* of the bias and wrong about which number is honest. The correct heuristic is procedural: **does this computation use only data observable at the moment of decision? If yes, it's clean. If no, it's biased — direction TBD.**

For the rest of the chapter and going into Ch11, we treat `trailing_sigma_thresh` as the bias-corrected baseline.

## §3 — Survivorship bias (named-only)

The textbook setup. You backtest a stock-picking strategy on the *current* S&P 500 for the period 2000-2026. Your universe is, by construction, the set of companies that *survived to 2026*. Lehman (delisted 2008), Bear Stearns (acquired 2008 in distress), Enron (delisted 2001), Pets.com (delisted 2000), GE (downgraded out of the Dow in 2018, fell substantially in S&P 500 weight): these names have catastrophic returns in their final years. A backtest that doesn't include them is silently averaging *only over the survivors* — and the survivors, by definition, did not experience catastrophe.

> **Definition — survivorship bias.** The systematic exclusion of failed or delisted entities from a backtest universe, leading to overestimated performance. The cleanest way to spot it: ask "what universe did this strategy have access to *as of the backtest start date*?" If the answer is "the universe as it exists today, projected backwards," the bias is present.

**Empirical magnitude.** Published research on US equities consistently finds that survivorship bias inflates measured Sharpe by 1-2% annualized — small per year, large in cumulative compounded returns. The exact figure depends on the universe and window; long-horizon backtests on small-cap universes can show inflations of 3-4%.

**Why our strategy is essentially immune.** We trade QQQ, an ETF tracking the NASDAQ-100. The ETF's price already reflects every constituent change — when an underperformer drops out of the NASDAQ-100, the ETF rebalances and its mark absorbs the cost. There is no "delisted ETF survivorship" issue at the ETF level itself. The same is true for SPY, IWM, and the other liquid index ETFs.

**When you'd need delisted data.** Any strategy that picks individual stocks: factor tilts, pairs trading, single-name event-driven strategies, microcap mean-reversion. For these, the standard data sources are:

- **CRSP** (Center for Research in Security Prices) — academic gold standard, expensive (institutional pricing); the source most asset-pricing papers cite.
- **Norgate Data** — independent vendor; survivorship-bias-free US equity history at retail-friendly pricing (~$50/month for end-of-day; intraday is more).
- **Sharadar** via Quandl / Nasdaq Data Link — mid-tier pricing, includes delisted history.

If you cannot get survivorship-clean data, the operational fix is to restrict the strategy to ETFs (where the bias is wrapped) or to design it specifically not to require constituent-level history.

## §4 — Snooping: a worked bug

The classic retail-quant move. Sweep an entry parameter — here `k_σ` — over a grid. Pick the value with the highest in-sample Sharpe. Quote that Sharpe as the strategy's edge.

This is **always** wrong. The "best" Sharpe in any sweep is the *order statistic* — the maximum — of a set of noisy estimates. By construction, the maximum of a noisy distribution exceeds the true expected value of the underlying estimator. Reporting the maximum without correction is reporting a noise high.

> **Definition — snooping bias.** Inflation of measured performance caused by selecting one parameter (or model variant) from many candidates evaluated on the same data. Synonyms: *data mining bias*, *p-hacking* (in academic statistics), *the multiple comparisons problem*. The mechanism is identical to the **multiple-testing problem** in classical statistics: when you run K hypothesis tests at the α = 0.05 level, the probability that *at least one* falsely "passes" is much greater than 0.05.
>
> **Definition — multiple-comparisons problem.** The general statistical issue that the false-positive rate for *any one* of K simultaneous tests at level α is approximately Kα, not α. Two corrections in common use: **Bonferroni** (raise the bar to α/K for every test — conservative; controls the family-wise error rate) and **Holm-Bonferroni** (sort the K p-values; compare the i-th smallest to α/(K - i + 1) — uniformly more powerful than plain Bonferroni; same family-wise error guarantee).
>
> *Where:*
> - α — the false-positive rate you want to guarantee for the *entire family* of tests, not for any individual one.
> - K — the number of tests run on the same data.
> - "family-wise error rate" — the probability that *at least one* test falsely passes when all nulls are true.

### What the experiment shows

We sweep `k_σ ∈ [0.5, 2.5]` in 21 evenly spaced steps, using the whole-sample σ scale (so we isolate the snooping bias from the look-ahead bias from §2). For each `k_σ` we record the trade count, in-sample annualized Sharpe, and t-statistic on per-trade mean PnL. The full sweep:

| k_σ  | Trades | Sharpe   | t-stat |
| ---- | ------ | -------- | ------ |
| 0.50 | 1,562  | **+1.86** | +1.84  |
| 0.70 | 1,276  | +1.78    | +1.76  |
| 1.00 |   900  | +0.82    | +0.78  | (Ch9's canonical anchor)
| 1.50 |   505  | +1.28    | +1.07  |
| 1.90 |   327  | −0.14    | −0.10  |
| 2.10 |   257  | **−1.83** | −1.22  | (worst)
| 2.50 |   157  | −1.22    | −0.69  |

(Full table in the notebook.)

Two findings, both stark.

### Snooping inflation is enormous

| Statistic                         | Sharpe |
| --------------------------------- | ------ |
| Sweep best (k_σ = 0.50)           | +1.86  |
| Sweep median across 21 thresholds | +0.82  |
| Sweep worst (k_σ = 2.10)          | −1.83  |

The "edge" the cherry-picked best-parameter Sharpe captures *over the median* is **+1.04 Sharpe**. That gap is entirely an artifact of the sweep — the strategy's underlying performance hasn't improved at all by considering more thresholds; we have just selected a noisy realization. The plan target was a snooping inflation of 0.3-0.7 Sharpe; reality on this data is 1.04. Course-correction: the bias is even bigger here than the spec's working target anticipated.

### The best parameter fails conventional significance — before any correction

The headline numbers:

| Bar                                                  | Critical \|t\| | Best \|t\| (sweep)  | Verdict |
| ---------------------------------------------------- | -------------- | ------------------- | ------- |
| Uncorrected α = 0.05                                 | **1.96**       | 1.84                | **FAILS** |
| Bonferroni at α / 21 ≈ 0.0024                        | **3.04**       | 1.84                | **FAILS** |
| Holm stepwise (smallest p vs α / 21, etc.)           | varies         | (no test passes)    | **FAILS** |

**Translation:** the most generous reading of the in-sample evidence — pick the best parameter from a 21-point sweep, ignore multiple-comparisons correction entirely, use the standard 95% bar — still does not produce a Sharpe whose mean per-trade PnL is statistically distinguishable from zero.

The "+1.86 Sharpe" headline is, statistically speaking, nothing.

The cost of having looked is captured by the gap between the uncorrected critical |t| of 1.96 and Bonferroni's 3.04. That gap grows with K (number of tests):

- K = 1 (no sweep) → 1.96
- K = 21 (this chapter) → 3.04
- K = 100 → 3.48
- K = 1,000 → 4.05
- K = 10,000 → 4.56

**Searching harder doesn't make finding easier — it makes it harder.** This is not a quirk of Bonferroni; it is a basic fact of probability under the null hypothesis. A more sophisticated correction (Holm, Benjamini-Hochberg) lowers the bar by a constant factor, not a logarithmic one.

The operational discipline:

> Sweep parameters in-sample only for *prototyping*. Quote the in-sample best Sharpe as the strategy's *upper bound* — the number reality cannot exceed. Out-of-sample performance is the only honest answer. Walk-forward (Ch11) is what gets you that number.

## §5 — Other biases worth naming

A briefer tour of biases the chapter doesn't work in detail. Each one inflates in-sample performance relative to what the live strategy will actually see; each one has a fix that costs you something (usually a less generous-looking backtest).

- **Liquidity bias** — backtesting at fills you'd never get on real flow: the mid-price, the perfect close, no spread, zero impact. Ch9's `next_open` execution removed the most blatant version of this (same-bar fill at the price the signal observed). The rest — bid/ask spread, partial fills, market impact at size — is Ch12's job.
- **Sample-period bias** — fitting on data dominated by one regime: a single bull market, a single low-vol year, a single rate-cut cycle. Ch11's walk-forward addresses this directly by forcing the strategy to operate across multiple non-overlapping windows. A single-window backtest, even one with honest mechanics and honest bias-correction, does not establish that the strategy works in any regime *other than the one it was measured in*.
- **Filtered-data bias** — quoting performance with the worst trades excluded. "We wouldn't have actually traded then because of the news, our intuition, a filter we'll add later." The "we didn't trade then" defense is almost always rationalized after looking at the trade. The fix is procedural: pre-register the filter rule before computing performance.
- **Optimization-stopping bias** — the human cousin of snooping. You start an optimizer, watch the in-sample Sharpe climb, and stop when "it looks right." The decision of when to stop *is* a multiple comparison — you implicitly considered every earlier stopping point and rejected it. The fix: pre-register a stopping rule (e.g., a fixed number of iterations, a held-out-set threshold).

The common thread: **every bias on the list inflates in-sample performance relative to what the live strategy will see.** That is not a coincidence. The reason is mechanical: any decision a backtester makes after looking at the data is, in effect, a parameter, and any parameter chosen to optimize a quantity on the data overfits that quantity.

## §6 — So what?

Decision rules this chapter unlocks:

1. **Compute every feature in the decision logic from data observable strictly before the decision time.** Whole-sample statistics (means, standard deviations, quantiles, regime labels) are the most common offenders. The fix is procedural: build the backtest as a one-pass loop where, at each bar, the only available data is everything before that bar.
2. **If your strategy needs an individual-stock universe, pay for survivorship-clean data.** CRSP, Norgate, or Sharadar. If you can't, restrict the strategy to ETFs.
3. **In-sample parameter sweeps are for prototyping only.** The best in-sample Sharpe across K thresholds is *always* an upper bound, never the strategy's actual edge. Quote it as "the largest number reality cannot exceed," not as "the strategy's performance."
4. **If you ran K backtests, the best one's t-statistic must beat ≈ Φ⁻¹(1 − α/(2K)) — Bonferroni's bar.** For K = 21 sweeps that bar is 3.04; for K = 100, it's 3.48. A best-of-K |t| of 1.84 — failing even the uncorrected 1.96 — is not evidence of edge no matter how dramatic the in-sample Sharpe looks.

What this chapter cannot yet tell you:

- **Whether the bias-corrected Sharpe survives out-of-sample.** Ch11 uses walk-forward refits (the strategy never sees a bar it hasn't been calibrated on yet) and reports the OOS Sharpe with bootstrap CI. That is the chapter's culminating number for the entire Ch8 → Ch11 deflation arc.
- **Whether the strategy survives realistic costs.** Ch12 stacks bid/ask spread, commission, and slippage on the bias-corrected backtest. Per-trade std on Ch9's ledger is ~7.4 bp; per-trade mean is ~0.2 bp. A 1 bp cost is 13× the mean. Ch12 will quantify which thresholds (if any) survive.

## Key Terms

| Term                       | Definition                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Bias (in backtesting)      | A structural feature of the simulation that shifts measured performance away from what a deployed strategy would see. |
| Look-ahead bias            | A decision uses information observable only after the moment of the decision — most often a whole-sample statistic. |
| Survivorship bias          | The universe excludes failed/delisted entities; only survivors are in-sample. Inflates returns on stock-pickers.   |
| Snooping bias              | Selecting one parameter from many candidates evaluated on the same data — the multiple-comparisons problem applied to backtesting. |
| Multiple-comparisons       | The statistical fact that K simultaneous α-level tests have family-wise false-positive rate ≈ Kα, not α.            |
| Bonferroni correction      | Raise each test's bar to α / K. Conservative; controls family-wise error.                                           |
| Holm-Bonferroni            | Sort p-values; compare i-th smallest to α / (K - i + 1). Uniformly more powerful than Bonferroni; same guarantee.  |
| In-sample (IS)             | A metric computed on the same data used to choose strategy parameters. Always an upper bound on truth.             |
| Parameter sweep            | A grid of parameter values evaluated on the same data, often as a prelude to selecting "the best" one.             |
| Point-in-time              | Discipline that decisions at time *t* use only data observable strictly before *t*.                                |
| Trailing-window estimator  | An estimator (often σ or μ) computed from the prior *L* observations, recomputed at each step. Point-in-time-clean. |

## Up next

**Ch11 — Backtesting III: Walk-forward and statistical validation.** Ch10's bias-corrected strategy still has its parameters chosen using *some* of the data — even with trailing σ, the chapter quoted in-sample numbers. Ch11 introduces the discipline of separating parameter selection from performance estimation: train/test splits, monthly walk-forward refits, and bootstrap CIs on out-of-sample PnL. The headline question — *does the strategy survive on data the strategy has never seen?* — gets its honest first answer there. The deflation arc Ch8 → Ch9 → Ch10 → Ch11 closes with whatever number the OOS Sharpe gives.

**Ch12 — Costs and slippage.** Once Ch11 has produced a credible OOS performance estimate, Ch12 stacks realistic frictions on top. Per-trade std is small enough that costs of even 1 bp per round-trip can flip the strategy from edge to nothing.

## Exercises

1. **Look-ahead bias on the holding period.** §2 demonstrated look-ahead on the threshold σ. Repeat the exercise for the *holding period* `K`. Sweep `K ∈ {1, 2, 3, 5, 10, 20}`. For each `K`, compute the in-sample best `k_σ` two ways: (a) using whole-sample σ, (b) using a trailing-60-session σ. Does the *chosen K* change between (a) and (b)? What does that tell you about the parameter's robustness across regimes? *Hint:* if K changes, the strategy's holding-period choice was sensitive to a mix of regimes the trailing version doesn't see.
2. **Two-dimensional snooping.** Sweep two parameters simultaneously: `N ∈ {1, 2, 3, 5}` and `k_σ` in 21 steps — 84 implicit tests. Compute the sweep's best Sharpe and apply Bonferroni at α / 84. Compare the corrected critical |t| to the one-dimensional case (3.04). The implicit test count grows as the *product* of grid sizes; small grids in 2D explode quickly. How quickly does the bar move when you go to 3D?
3. **Holm vs Bonferroni.** Holm's stepwise correction is uniformly more powerful than Bonferroni — it accepts any subset Bonferroni accepts, sometimes more. Re-do §4 with the actual Holm procedure (smallest p compared to α/K, second-smallest to α/(K-1), …, largest to α/1). Does the conclusion change on this data? Why or why not? *Hint:* think about what Holm *cannot* do that Bonferroni *also* cannot.
