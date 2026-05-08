# Chapter 9 — Backtesting I: Building an Honest Backtest

Chapter 8 ended on a number — annualized Sharpe of **+2.08** on QQQ closing-window mean reversion — and an explicit warning: don't believe it yet. This chapter is the first instalment of the cure.

The strategy is the same as Ch8's: in the last 30 minutes of QQQ's regular trading session, *N* = 1 minute prior log return crosses ± 1.0 σ; we **fade** (signal = −sign(prior return)); we hold *K* = 3 minutes; we exit. Same data, same parameters, same inputs. Only the **mechanics of the simulation** change.

What we will find is that a substantial fraction of Ch8's headline Sharpe was an artifact of how the backtest was run, not what the strategy actually did. Specifically, two mechanical issues:

1. **Same-bar execution.** Ch8 used the close of bar *t* both to compute the signal *and* to enter the trade. That is not realistic — you cannot fill an order at a price you have not yet observed.
2. **Overlapping positions.** Ch8's vectorized backtest counted every signal bar's contribution to PnL as if it were a separate trade. In a real account you can only hold one position at a time (per side) — you cannot stack ten 3-minute trades on top of each other minute by minute.

Fixing both lops the in-sample Sharpe roughly in half, from +2.08 (Ch8) to about **+0.80** (this chapter, `next_open` execution). And then a bootstrap on the trade ledger reveals the *real* news: the 95% CI on that +0.80 is approximately **(−1.3, +2.7)** — comfortably including zero. Even the corrected number is not statistically distinguishable from random on a single year of data.

That is honest mechanics. It is necessary, not sufficient. It does not yet address whether the strategy survives **bias** (Ch10 — overfitting, look-ahead in the σ used as the threshold, multiple-testing correction on the (*N*, *K*) sweep) or **out-of-sample** (Ch11 — walk-forward and refit). Honest mechanics is the foundation those chapters build on; without it, every later result inherits the bug.

## Three things this chapter covers

1. **Vectorized vs event-driven backtests.** The vectorized PnL is a series of (signal × forward-return) products computed in one shot over the whole dataset. The event-driven backtest loops bar-by-bar with explicit position state, entry orders, exit orders, and a trade ledger. Each style has bugs the other doesn't, but only the event-driven loop *forces* you to confront the questions a real account would.
2. **Point-in-time discipline.** A signal computed at the close of bar *t* must execute at or after the open of bar *t*+1. Vectorized backtests can violate this silently; event-driven ones make the violation impossible to hide (the loop ordering is the discipline). We will run the same strategy under three execution-timing assumptions and read off how much Sharpe each costs.
3. **Trade-level metrics with bootstrap CIs.** Aggregate PnL is one number; the *distribution* of per-trade outcomes is the actual evidence. A bootstrap on the trade ledger gives a 95% CI on Sharpe, expectancy, and profit factor — and that CI tells you whether the strategy is statistically distinguishable from noise. Ch5 used the bootstrap on daily SPY returns; here we apply the same idea to the trades themselves.

> **Definition — backtest.** A simulation of a trading strategy on historical data. The backtest takes a rule (entry, exit, sizing) and a time series of prices, walks through history applying the rule, and produces a PnL stream you can analyze the same way you would analyze a real trading record.
>
> **Definition — vectorized backtest.** A backtest that computes signals and PnL for every observation in the dataset at once using array operations, with no notion of "now" advancing through time bar-by-bar. Fast and easy to write, easy to get wrong in ways an event-driven engine would catch.
>
> **Definition — event-driven backtest.** A backtest that loops bar-by-bar through the data, maintaining explicit position state and processing entries and exits as they would occur in real time. Slower to write, harder to get *wrong* in subtle ways — execution timing, position management, and order-of-operations bugs all have to be coded explicitly.
>
> **Definition — trade ledger.** The chronological list of completed trades produced by an event-driven backtest. Each row records entry timestamp, exit timestamp, entry price, exit price, side, and PnL. The ledger is the unit of analysis from §4 onward — every metric in the chapter is computed from it.

## §1 — Why the vectorized backtest lies

Ch8's vectorized PnL was, in spirit:

```
signal_t      = -sign(prior_N_t)   if |prior_N_t| > k_sigma * sigma
trade_pnl_t   = signal_t * next_K_t
total_pnl     = sum(trade_pnl over all signal bars)
```

where `prior_N_t` is the log return ending at the close of bar *t*, `next_K_t` is the log return from the close of bar *t* to the close of bar *t* + *K*, and the threshold σ is the standard deviation of `prior_N` across the closing-window observations.

Look closely at the boundary. `prior_N_t` ends at close[*t*]. `next_K_t` starts at close[*t*]. The same close[*t*] is used both to *decide* the trade and to *fill* it. In real trading that is impossible: at the moment close[*t*] becomes observable, the bar is already over and there is no liquidity left at that price. Whatever fill you actually get is at the next available print, and the next available print is **open[*t* + 1]**, one minute later.

This particular bug — sometimes called **bar-boundary look-ahead** — is one of the most common bugs in vectorized backtests. It is not visible unless you specifically check, because the math runs cleanly: `next_K_t` is a real number that pandas computes without complaint. The bug shows up as a Sharpe number that is too good.

> **Definition — point-in-time.** The discipline that, at each instant *t* of a backtest, only data observable strictly *before* time *t* is allowed to inform decisions made at time *t*. A point-in-time-correct signal at close[*t*] uses no information from times ≥ *t*. Vectorized backtests have to enforce this with explicit lags; event-driven backtests enforce it by the order in which the loop processes bars.
>
> **Definition — fill assumption.** The rule that converts a *decision* (the signal said "buy") into an *execution price* (you actually paid X). Common fill assumptions: market-on-close (fill at the close of the signal bar — usually wrong unless the order was placed before the close), next-open (fill at the open of the bar after the signal — the simplest defensible assumption), VWAP-of-next-K-minutes (a more realistic proxy for a sized order), midquote (a finer assumption usable when bid/ask are available).
>
> **Definition — execution timing.** The choice of *which* bar's *which* price counts as the fill. We will compare three execution timings in §3: same-close, next-open, next-close. Each is a different fill assumption.

## §2 — The event-driven backtest skeleton

The event-driven loop has the structure of a real trading day. We iterate sessions; within each session, we iterate minute bars in chronological order. At each bar, in order:

1. **Exit check.** If we are in a position and have held it *K* bars, exit. Choose the exit price according to the execution-timing rule.
2. **Entry check.** If we are flat, the time gate is open (`360 ≤ minute_of_session < 386`), and the prior-1-min log return crosses ± threshold, take the trade. Choose the entry price according to the execution-timing rule.
3. **Session-end flatten.** If the loop reaches the last bar of the session and we are still in a position, force-flatten at the last close. (No overnight exposure — the strategy is intraday by construction.)

The exit-before-entry order matters. Without it, on a bar where an exit and a fresh entry both fire, we would silently increase position size; the loop would re-enter while still long. Putting exits first makes the model "flat-between-trades" by construction.

The whole loop fits in roughly 50 lines. The notebook (`lesson.ipynb`) has the actual implementation; the structure is:

```python
def event_driven_backtest(rth_df, exec_timing, threshold, N=1, K=3,
                          entry_start=360, entry_end=389):
    trades = []
    for date, day in rth_df.groupby("session_date"):
        day = day.sort_index().reset_index(drop=True)
        in_pos, entry_i, entry_px, entry_ts = 0, None, None, None
        for i in range(len(day)):
            mos     = day.loc[i, "minute_of_session"]
            close_i = day.loc[i, "close"]
            # 1. exit check
            if in_pos != 0 and (i - entry_i) >= K:
                exit_px = pick_exit_px(day, i, exec_timing)
                trades.append({...})
                in_pos = 0
            # 2. entry check
            if in_pos == 0 and entry_start <= mos < entry_end - K and i >= N:
                prior_N = np.log(close_i / day.loc[i - N, "close"])
                if abs(prior_N) > threshold:
                    side = -1 if prior_N > 0 else +1
                    entry_px = pick_entry_px(day, i, exec_timing)
                    in_pos, entry_i = side, i
        # 3. session-end flatten
        if in_pos != 0:
            trades.append({"exit_px": day.iloc[-1].close, ...})
    return pd.DataFrame(trades)
```

That is the entire mechanism. Three branches and a flatten. Notice what is *not* there: no library, no class hierarchy, no "engine." The point of writing it by hand is to make every assumption visible. When something looks wrong in §3's table, the bug is in this 50-line function and not buried in a third-party config file.

### The trade-count surprise

Running the loop on the QQQ 1-min cache (one year of RTH bars, 251 sessions, 95,318 bars) yields a trade ledger of **914 trades** under each of the three execution timings. Ch8's *vectorized* backtest on the same strategy reported **1,471 trades**.

That is not a minor discrepancy — it is roughly a 38% difference, on the same underlying strategy and the same data. The cause is the position-management rule: vectorized PnL counts every signal-bar's contribution, even when those bars overlap in time. If the signal fires at minute 360 and again at minute 361, Ch8's vectorized accounting books *two* "trades" — one held from 360 to 363, one held from 361 to 364 — even though in a single account those are not two independent trades; they are effectively one position with a marginal adjustment.

The single-position event-driven version drops the second of any pair of overlapping signals. That is what a real account would do; it is also what Ch10 onwards inherits. The takeaway is not that one count is "right" and the other "wrong" — it is that the word "trade" means something different in each. When someone hands you a backtest report, ask which one the trade count is.

## §3 — Three execution timings, side by side

Same loop, same data, three assumptions about *when* the trade prints:

| Timing       | Entry price            | Exit price             |
| ------------ | ---------------------- | ---------------------- |
| `same_close` | close of signal bar    | close of exit bar      |
| `next_open`  | open of bar after sig  | open of bar after exit |
| `next_close` | close of bar after sig | close of bar after exit |

`same_close` is Ch8's vectorized timing rebuilt event-driven (same bug, isolated). `next_open` is the cleanest defensible point-in-time rule: signal observed at close[*t*], fill at open[*t* + 1]. `next_close` is a one-bar-later proxy — the price has had a full minute to drift after our signal fired and before we got filled. We can read the gap between `next_open` and `next_close` as a coarse "slippage" estimate.

The notebook tabulates all three. The headline numbers:

| Timing       | Trades | Hit rate | Profit factor | Annualized Sharpe |
| ------------ | ------ | -------- | ------------- | ----------------- |
| `same_close` | 914    | 0.501    | 1.150         | **+1.57**         |
| `next_open`  | 914    | 0.492    | 1.073         | **+0.80**         |
| `next_close` | 914    | 0.503    | 1.069         | **+0.79**         |

**Reading the table.** `same_close` Sharpe is roughly twice `next_open` Sharpe. Half of Ch8's headline Sharpe was paid for by the same-bar bug. There is nothing exotic about this gap — it is the difference between "buy at the price you see" and "buy at the next observable price." On strategies with a 1-minute holding period and edge measured in fractions of a basis point per trade, that distinction dominates the result.

`next_open` is the row downstream chapters inherit. Ch10 will sit on this number, demonstrate which of *its* assumptions are still biased (the σ used in the threshold is computed with full-sample look-ahead; the (*N*, *K*) was selected by sweeping), and shrink it further. Ch11 will run the bias-corrected strategy out-of-sample on a walk-forward schedule.

`next_close` ≈ `next_open`. The "one-bar slippage" framing turns out not to bite at 1-minute resolution, because the open and the close of the same minute usually agree to within a few hundredths of a percent. That is honest: at this bar length, you do not buy realism by shifting one bar later. Realistic slippage modeling needs a basis-point haircut and an explicit cost function — the topic of Ch12. Treating `next_close` as a slippage proxy is a heuristic, not a model.

## §4 — Trade-level metrics on the canonical ledger

From here on, the **canonical ledger** is `next_open`: 914 trades across 230 sessions, mean per-trade log return ≈ +1.9 bp, per-trade std ≈ 7.4 bp.

The metrics we computed in Ch5 and Ch7 — Sharpe, max drawdown, expectancy, profit factor, payoff ratio — all apply directly to a trade ledger; the only adjustment is how to **annualize** the per-trade Sharpe.

> **Definition — annualizing trade-level Sharpe.** Per-trade Sharpe = mean / std of the per-trade PnL series. To convert to an annualized figure, multiply by √(trades per year). Trades per year here is `trades_in_window × (252 / sessions_in_window)`. With 914 trades over 230 sessions that is roughly 1,001 trades per year, so √(tpy) ≈ 31.6. Per-trade Sharpe of about 0.025 then annualizes to ≈ +0.80.
>
> *Where:*
> - `mean / std` — sample moments of the per-trade PnL column of the trade ledger.
> - `trades per year` — number of trades the strategy fires in 252 trading days, estimated as `n_trades × (252 / n_sessions)`. This assumes the strategy's trade-firing rate is roughly stationary across the year.
> - `√(tpy)` — the same √*t* rule from Ch1 §3, applied to the trade clock instead of the calendar clock.

The canonical-ledger summary:

| Metric              | Value      |
| ------------------- | ---------- |
| Trades              | 914        |
| Hit rate            | 0.492      |
| Mean PnL (log)      | +1.9 e−5   |
| Per-trade std (log) | +7.4 e−4   |
| Profit factor       | 1.073      |
| Payoff ratio        | 1.092      |
| Annualized Sharpe   | **+0.80**  |
| Max drawdown (log)  | −2.0%      |
| Expectancy (R)      | +0.037     |
| Sessions            | 230        |
| Trades per year     | 1,001      |

A point estimate of +0.80 is in tradable territory by retail intraday standards — *if* it is real. The next section asks how confident we should be that it is.

## §5 — Bootstrap CI on the trade ledger

The Ch5 lesson re-applies. A point Sharpe is one realization of a noisy estimator; without a confidence interval, you cannot tell whether the strategy is genuinely different from a random one of the same hit rate and payoff structure.

The bootstrap is the most direct way to get the CI. Algorithm:

1. Treat the trade ledger as the population.
2. Resample with replacement to get a bootstrap ledger of the same size.
3. Compute annualized Sharpe on the resample.
4. Repeat 2,000 times.
5. The 95% CI is the central interval — 2.5th and 97.5th percentiles — of the 2,000 resampled Sharpes.

Running this on the canonical ledger produces:

| Block size | 95% CI               | Width |
| ---------- | -------------------- | ----- |
| 1          | (−1.29, +2.73)       | 4.02  |
| 5          | (−1.20, +2.70)       | 3.90  |
| 20         | (−1.26, +2.97)       | 4.23  |

> **Definition — block bootstrap.** A bootstrap that resamples *contiguous blocks* of length *b* rather than individual observations. For *b* = 1 the block bootstrap is equivalent to the i.i.d. bootstrap. Larger blocks preserve serial correlation in the ledger; if outcomes cluster (consecutive trades win or lose together), block-1 will under-estimate variance and block-*b* will give a more conservative CI. Comparing widths across block sizes is a serial-dependence diagnostic.

**Two findings in this table.**

First, **the CI for the canonical Sharpe straddles zero.** A point estimate of +0.80 with 95% CI (−1.29, +2.73) means the data, on a single year, cannot rule out that the strategy's true Sharpe is negative. That is a striking result for what looked like a tradable headline number. The pedagogical lesson: when someone reports a Sharpe without a CI, you *do not yet know* whether the strategy is better than nothing.

Second, **block size barely changes width.** Block-1, block-5, and block-20 all give ≈ 4-wide intervals. That is itself a result: per-trade outcomes are not strongly autocorrelated. If trades came in win-streaks and loss-streaks, block-20 would inflate the CI relative to block-1; instead they look essentially independent. So an i.i.d. bootstrap on the ledger is fine here — and we now have *evidence* that it is fine, not just an assumption.

This is the "essentially independent at the trade level" property of closing-window MR specifically. It is not a general fact about all strategies. Ch11 will re-run the bootstrap on **daily PnL** instead of per-trade PnL — daily PnL inherits the day's market regime, and there block size *does* matter. Different unit of analysis, different bootstrap structure, different CI.

## §6 — Diagnostic plots

The notebook produces three views of the canonical ledger; they each catch a different category of error.

1. **Per-trade PnL histogram.** Shape, asymmetry, and outliers. A strategy with a Sharpe of +0.80 should look "barely positively shifted" — a roughly symmetric distribution with a slight rightward bias of the mean against zero. If the histogram had an obvious fat right tail (a few big winners pulling up the mean) we would worry about a robust-mean check; if it had a fat left tail (one disaster), we would worry about whether the disaster was data-error.
2. **Cumulative PnL with drawdown overlay.** The cumulative log PnL should rise smoothly across the year. The drawdown overlay (the red shaded region between cumulative and running peak) should not exhibit one giant cliff that swallowed all gains; if it does, the strategy depends on a single event surviving. The MDD here is roughly −2% (in log return terms, on the cumulative PnL series).
3. **Monthly aggregate PnL.** Bar chart, one bar per calendar month. This is regime-stability. A strategy that is +0.80 Sharpe by averaging two amazing months and ten flat ones is structurally more fragile than one that is +0.80 by being slightly positive in most months. The monthly view also catches obvious data joins — if month *X* has 50× the PnL magnitude of every other month, look at the data.

These three plots, together, are what the chapter calls "knowing what your strategy actually did." A backtest that has been distilled to a single Sharpe number has thrown away most of the information you need to decide whether to deploy it.

## §7 — So what?

Decision rules this chapter unlocks:

1. **Always re-run a vectorized backtest in event-driven form before believing the headline.** If the two disagree by more than ~10–20% in Sharpe, the vectorized version has a point-in-time bug. The fix is mechanical, not subtle.
2. **Quote a CI, not a point estimate.** If the 95% CI on Sharpe straddles zero on the in-sample window, the strategy is not yet a strategy — it is a hypothesis. Walk-forward (Ch11) is the way to test it.
3. **Audit the trade-count.** If two backtests of "the same strategy" disagree on how many trades it makes, they are not the same backtest. Find the position-management or execution-timing assumption that differs and pick the realistic one.
4. **Plot the trade-PnL histogram and the monthly bar chart.** A point Sharpe and an aggregate cumulative line do not catch shape problems or regime concentration. Two more plots is a tiny price for catching a strategy that survives by averaging across two good months.

What this chapter cannot yet tell you:

- **Whether the strategy is overfit.** The (*N*, *K*) sweep in Ch8 §1, the threshold σ computed with full-sample look-ahead, and the choice of the closing-window time gate were all selections from the same data we are evaluating on. Ch10 quantifies the bias each one introduces and demonstrates the corrections — trailing σ for the threshold, multiple-comparison adjustment for the parameter sweep.
- **Whether the strategy survives out-of-sample.** A single-window backtest, even with honest mechanics and a CI, gives no out-of-sample evidence. Ch11 runs the strategy with a walk-forward refit schedule on QQQ across multiple non-overlapping windows; the *out-of-sample* Sharpe with bootstrap CI is the next-strongest evidence after this chapter.
- **Whether the strategy survives realistic costs.** Per-trade std is ~7.4 bp; mean is ~0.2 bp. Ch12 shows that a 1 bp spread + commission cost is enough to push the canonical strategy's expectancy across zero. Costs are not "an adjustment after the fact" — they are the gate the strategy has to pass.

## Key Terms

| Term                    | Definition                                                                                                             |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Backtest                | Simulation of a trading strategy applied to historical price data.                                                     |
| Vectorized backtest     | Backtest computing all signals and PnL contributions in array operations without iterating bar-by-bar.                 |
| Event-driven backtest   | Backtest looping bar-by-bar with explicit position state, entry orders, exit orders, and a trade ledger.               |
| Trade ledger            | Chronological list of completed trades with entry/exit timestamps, prices, side, and PnL — the unit of analysis.      |
| Point-in-time           | Discipline that decisions made at time *t* use only data observable strictly before *t*.                               |
| Fill assumption         | Rule converting a decision into an execution price. Common: same-close, next-open, next-close, VWAP, midquote.        |
| Execution timing        | Choice of *which* bar's *which* price counts as the fill. This chapter compares same-close, next-open, next-close.    |
| Bar-boundary look-ahead | Specific bug where the closing price of bar *t* is used in both the signal computation and the fill at time *t*.       |
| Block bootstrap         | Bootstrap that resamples contiguous blocks of length *b* — preserves serial correlation; *b* = 1 is the i.i.d. case.   |
| Slippage                | Difference between the price implied by the signal and the actual fill price. Costs and partial fills both contribute. |
| Single-position rule    | Position-management rule that allows at most one open trade per side at a time. Drops overlapping signals.             |

## Up next

**Ch10 — Backtesting II: Bias and data integrity.** We hand Ch10 the canonical `next_open` ledger and ask: which of *its* inputs were chosen with knowledge of the answer? Whole-sample σ in the threshold (look-ahead). Whole-sample (*N*, *K*) sweep (selection bias / multiple comparisons). Survivorship bias (named only at our scale; relevant when adding tickers). The deflation arc continues: each correction gives back a fraction of Sharpe.

**Ch11 — Backtesting III: Walk-forward and statistical validation.** Ch11 takes the bias-corrected strategy and runs it with a monthly refit on a multi-year QQQ window. Out-of-sample Sharpe with bootstrap CI. The question this chapter could not answer — "is this strategy real?" — gets its honest first answer there.

## Exercises

1. **SPY transfer.** Re-run the three-timings table on SPY 1-min (path: `../06-bridge-to-intraday/data/spy_1min.parquet`). Does the same-bar → next-open Sharpe gap have the same magnitude as on QQQ (~50%)? If different, what about SPY versus QQQ would change the size of the bug? *Hints:* compare per-trade std and trade count; SPY's lower volatility may produce smaller signal magnitudes relative to costs.
2. **Where slippage actually shows up.** The chapter noted that `next_close` ≈ `next_open` at 1-minute bars because intra-bar drift is small. What would change at 5-second bars? At 5-minute bars? Sketch (or simulate, if you resample the cache) the relationship between bar length and the `next_close` − `next_open` Sharpe gap. Connect to Ch12's coming cost framework. *Hint:* the slippage proxy "cost" in Sharpe units scales roughly with the within-bar price drift relative to the per-trade PnL std.
3. **Block bootstrap structure.** The block-size sweep above (1, 5, 20) gave nearly identical CI widths on the *trade ledger*. Now aggregate the canonical ledger to **daily PnL** (sum of per-trade PnL within each `session_date`) and bootstrap with block=1, 5, 20 again. What changes, and why? When should you start to suspect that block size matters?
