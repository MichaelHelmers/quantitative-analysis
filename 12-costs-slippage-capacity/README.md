# Chapter 12 — Costs, Slippage, and Capacity

The Ch8→Ch11 deflation arc closed with **walk-forward OOS Sharpe of +0.88, 95% CI ≈ (−1.6, +3.5)** — positive point estimate, CI straddling zero. Every Sharpe in that arc was a *zero-cost* number. Ch12 stacks the frictions a real broker imposes: bid/ask spread, commission per trade, and slippage (market impact). The chapter answers the question the deflation arc has been moving toward: **does the strategy survive realistic execution?**

The strategy's per-trade mean PnL on Ch11's walk-forward ledger is roughly **0.2-0.5 bp**, with per-trade std ~7 bp. A 1 bp round-trip cost is several times the per-trade mean. The cost wedge is *not* a small correction. It is the dominant term.

Three flavors of cost:

1. **Explicit cost** — what hits your statement. Commission, exchange/SEC fees, financing on overnight inventory. Visible, billed, easy to model.
2. **Implicit cost** — what you pay through prices. Bid/ask spread (you cross it on entry and exit), and slippage (your own size walks the next print further from where you wanted to fill). Invisible on the statement; first-order on small-edge strategies.
3. **Capacity** — the size beyond which your own slippage eats the edge. Defined by setting expected slippage equal to per-trade mean PnL.

This chapter measures all three on QQQ 1-min data, then re-runs Ch11's threshold sweep with after-cost Sharpe as the objective. The verdict — flagged here so the rest of the chapter is read with eyes open — is that **the strategy is unprofitable at every threshold, with capacity Q\* = $0**. The cost wedge alone exceeds the per-trade edge. This is the strongest possible form of "your edge isn't real."

## Three things this chapter covers

1. **Effective spread without a quote feed.** §2. Roll's (1984) estimator recovers half-spread from the lag-1 autocovariance of trade returns. Corwin-Schultz (2012) recovers it from two-bar high-low ranges. Both run on the same 1-min OHLCV cache the rest of the curriculum uses. The two estimators agree to within 10% on QQQ — **Roll's all-RTH = 0.72 bp, Corwin-Schultz = 0.79 bp** — and the agreement is itself the chapter's confidence statement.
2. **Cost as a function of size: the square-root impact law.** §4. Impact = η · σ<sub>d</sub> · √(Q/ADV). For QQQ at $30k notional, impact is **0.014 bp** — below the noise floor of every other cost. At $10M notional, impact is **0.26 bp** — comparable to half-spread. Impact only matters at institutional size.
3. **Cost-aware optimization changes the optimal threshold.** §6. The cost-naive `k_σ*` (which maximizes pre-cost Sharpe) is **0.70**; the cost-aware `k_σ*` is **2.20**. The cost-naive choice produces the *worst* after-cost performance because it maximizes trade count, and trade count is what costs are levied against. Even the cost-aware optimum is **negative**: S_post = −2.97.

> **Definition — half-spread.** Half the inside bid/ask spread, expressed as a fraction of price (or in bp). The one-leg cost of crossing the spread once — buying at the ask or selling at the bid instead of executing at the mid.
>
> **Definition — explicit cost.** Costs that hit your brokerage statement — commission, exchange fees, SEC fees, financing on margin and overnight inventory.
>
> **Definition — implicit cost.** Costs paid through prices, not the statement — the half-spread you cross and the impact your size induces.
>
> **Definition — strategy capacity.** The largest trade size Q\* at which the strategy's after-cost expectancy is still non-negative. Above Q\*, your own slippage produces a loss in expectation; below Q\*, the per-trade mean covers all costs.

## §1 — The Ch11 ledger meets reality

Per-trade statistics from Ch11's walk-forward OOS ledger (575 trades over 148 sessions, the strategy's most honest pre-cost characterization):

- per-trade mean ≈ **0.16 bp**
- per-trade std ≈ **7.4 bp**
- pre-cost annualized Sharpe ≈ **+0.88** with 95% CI ≈ (−1.6, +3.5)

When we re-run the strategy in this chapter against the full 1-year sample to produce comparable per-trade stats, at `k_σ = 1.0` we get **per-trade mean = +0.32 bp**, **std = 6.9 bp**, **892 trades** — slightly higher mean than Ch11's walk-forward number because we are using the full sample rather than only OOS windows. Use **0.3-0.5 bp** as a working figure for the chapter's per-trade-mean budget at retail sizes; the exact number depends on k_σ and on whether you're looking at IS or OOS.

The cost budget is whatever fraction of 0.3-0.5 bp we can spend without making the after-cost expectancy negative. That budget is **tiny**. The cleanest expression of the chapter's question is: at what cost level does after-cost expectancy cross zero?

## §2 — Effective spread without a quote feed

Bid/ask spread is the cleanest first-order implicit cost. On free retail data feeds (Alpaca's IEX feed, Yahoo, Polygon-free), you only see trade prints — no quote-by-quote bid/ask. We need an estimator that recovers the *effective* spread from trade prices alone.

### Roll's (1984) estimator

If trades bounce randomly between bid and ask but the *true* (mid) price follows a random walk, then consecutive trade returns have a mechanical negative autocovariance: a trade at the ask followed by a trade at the bid produces a negative return that does not reflect any change in fair value. Roll proved the expected lag-1 autocovariance of trade returns equals **−s²**, where *s* is the effective half-spread.

> **Formula — Roll's effective half-spread.**
>
> *s* = √(−Cov(r<sub>t</sub>, r<sub>t−1</sub>)) when the lag-1 covariance is negative
>
> where:
> - *r<sub>t</sub>* = log return between consecutive trade prices (here, 1-min closes treated as trade prints)
> - Cov is the sample lag-1 autocovariance (unitless if *r* is a fraction)
> - *s* is in the same units as *r* (fraction of price); multiply by 1e4 for bp
>
> If the lag-1 covariance is positive, Roll's is undefined — typically because real momentum or mean-reversion dominates over bid-ask-bounce noise. On 1-min QQQ data the covariance is negative everywhere we look.

### The Ch7 connection — the chapter's reframing

Roll's estimator and Ch7's lag-1 ρ measure the same statistic, just rescaled. Ch7 found QQQ all-RTH lag-1 ρ = −0.028. If you partition that ρ into mechanical bid-ask-bounce noise and real economic mean-reversion, Roll's gives you the noise component; the residual is the signal Ch7's strategy is harvesting. So Roll's is an *upper bound* on the true effective spread — some of the negative lag-1 ρ is genuine MR that Roll's miscounts as spread.

The three subsamples we computed on QQQ 1-min:

| Window | half-spread (bp) | Ch7's lag-1 ρ |
|---|---|---|
| All RTH | **0.72** | −0.028 |
| Closing 30 min (Ch7's MR-strongest window) | **0.54** | −0.067 |
| Midday (60-299 min into session) | **0.71** | −0.035 |

**The closing window has *lower* effective spread than all-RTH, not higher.** That is mildly surprising — Ch7 found closing's lag-1 ρ ≈ 2× midday's, and Roll's mechanically scales with |ρ|. If the closing window's larger ρ were mostly bid-ask noise, closing's Roll's would be larger too. It isn't. **The closing window has both a stronger MR signal *and* a smaller noise floor.** Most of Ch7's closing-window lag-1 ρ is genuine economic mean-reversion, not spread artifact.

This is also a methodology note worth carrying. Roll's gives an **upper bound** because it cannot separate genuine MR from bid-ask noise. The cleaner the genuine MR signal, the more Roll's *over-estimates* the spread. A second estimator — Corwin-Schultz — gives an independent sanity check.

### Corwin-Schultz (2012) — second opinion

Corwin-Schultz extracts the spread from the high–low *range* of two consecutive bars. The intuition: over a short window, the high is more likely a buyer-initiated print (near the ask) and the low a seller-initiated print (near the bid). The expected log(H/L) inflates by approximately the spread on top of true within-bar volatility. Subtracting the variance contribution (calibrated from the two-bar combined range) leaves the spread.

> **Formula — Corwin-Schultz half-spread (per two-bar window).**
>
> β = (log(H<sub>t</sub>/L<sub>t</sub>))² + (log(H<sub>t+1</sub>/L<sub>t+1</sub>))²
>
> γ = (log(max(H<sub>t</sub>, H<sub>t+1</sub>) / min(L<sub>t</sub>, L<sub>t+1</sub>)))²
>
> α = (√(2β) − √β) / (3 − 2√2) − √(γ / (3 − 2√2))
>
> spread = 2 (e<sup>α</sup> − 1) / (1 + e<sup>α</sup>)
>
> where:
> - *H<sub>t</sub>*, *L<sub>t</sub>* are the high and low of bar *t* (price units; the log ratios are unitless)
> - *β* uses each bar's own H/L range squared; *γ* uses the combined two-bar range squared
> - the constants 3 − 2√2 ≈ 0.172 calibrate the H/L spread of a Brownian price path under continuous trading
> - *spread* is the full bid/ask spread as a fraction of price; divide by 2 for half-spread; multiply by 1e4 for bp

**Caveat:** Corwin-Schultz was derived for *daily* bars. We adapt it to 1-min bars; the underlying H/L-from-Brownian-motion derivation assumes continuous trading within the bar, an approximation that degrades on thinly-traded names. For a liquid ETF like QQQ at 1-min, prior empirical work finds the adaptation tracks consolidated spreads within a few tens of bp.

On QQQ, the result is:

| Estimator | Half-spread (bp) |
|---|---|
| Roll's, all RTH | **0.72** |
| Corwin-Schultz, all RTH | **0.79** |

Within 10%. We adopt **0.72 bp (Roll's all-RTH)** as the chapter's working half-spread number.

## §3 — Explicit cost: commission

Commission is the most predictable cost and easiest to size. Three reference points for retail QQQ execution in 2026:

| Broker | Structure | Per-share | $30k notional (~43 shares) | bp on $30k |
|---|---|---|---|---|
| Schwab / Fidelity / Robinhood | Zero (PFOF) | $0 | $0.00 | **0.000** |
| IBKR tiered | Per-share | $0.0035–$0.005 | $0.15–$0.22 | **0.05–0.07** |
| IBKR fixed | Min $1/order | $0.005 capped | $1.00 | **0.33** |

> **Definition — payment for order flow (PFOF).** A retail broker routes the customer's order to a wholesale market maker (Citadel, Virtu) rather than to the public lit exchange. The market maker pays the broker a fraction of a cent per share for the order flow; the customer receives some price improvement vs the National Best Bid and Offer — typically 0.01-0.04 bp on a $30k QQQ trade — but cannot directly observe whether the improvement covers what the broker received. PFOF makes "zero commission" possible; it shifts the cost into the spread the wholesaler captures.

The right reference for an honest cost model is **IBKR tiered at $0.005/share ≈ 0.07 bp per leg** — large enough to be a realistic worst case for someone who is *not* on PFOF, small enough to be representative of efficient retail execution. We use 0.07 bp per leg as the chapter's commission number.

## §4 — Implicit cost: slippage and the square-root impact law

When your buy order is large relative to the resting size on the offer, you walk up the book — first share fills at the inside ask, next at the next price level, etc. The *executed* average is worse than the inside ask by an amount that scales with order size. This is **market impact**.

The empirical regularity, robust across markets and decades of TAQ studies (Almgren-Chriss 2000; Almgren et al. 2005; later replicated on equities, FX, futures): temporary impact scales with the **square root** of the order's fraction of average daily volume.

> **Formula — square-root impact law (per leg).**
>
> impact = η · σ<sub>d</sub> · √(Q / ADV)
>
> where:
> - *η* is the **impact coefficient**, empirically ≈ 0.1 for liquid US equities (Almgren et al. 2005); 0.3 conservative; 0.5 illiquid microcap territory
> - *σ<sub>d</sub>* is **daily volatility** of the underlying (fraction; e.g., 0.01 for 1%)
> - *Q* is the order's dollar size (USD)
> - *ADV* is **average daily dollar volume** of the underlying (USD)
> - *impact* is in the same units as σ<sub>d</sub> (fraction); multiply by 1e4 for bp
>
> Multiply by 2 for a round-trip (entry + exit).

**Why square root, not linear?** Two informal intuitions. (1) Above some "good" size, you need patience — you cannot pull all the liquidity at the inside immediately, you wait for resting orders to refresh. Doubling the size doesn't double impact because liquidity arrives stochastically and partially fills you at favorable prices. (2) Dealer inventory risk scales with √variance, so dealers price impact accordingly. Both intuitions land at the same √ exponent.

### Per-leg impact at varying Q (QQQ, consolidated ADV $15B)

| Q (USD) | η=0.1 | η=0.3 |
|---|---|---|
| $10,000 | 0.008 bp | 0.025 bp |
| $30,000 | **0.014 bp** | 0.043 bp |
| $100,000 | 0.026 bp | 0.079 bp |
| $1,000,000 | 0.084 bp | 0.251 bp |
| $10,000,000 | 0.265 bp | 0.794 bp |

### Data caveat: IEX feed vs consolidated tape

The ADV computed directly from Alpaca's IEX feed is **$0.44B/day** — about 3% of the consolidated tape's **~$15B/day** for QQQ in 2025-2026. The IEX feed only reports IEX-routed prints; consolidated tape spans all 16 US equity venues. For the impact equation we use the **consolidated $15B** denominator because that is the full liquidity pool a real order would access. The IEX figure is what our data shows; the consolidated figure is what reality is.

Three takeaways from the impact table:

1. **At $30k notional, impact is 0.014 bp.** Below the noise floor of every other cost component. A retail-sized trader on QQQ pays essentially nothing in impact.
2. **At $1M notional, impact is 0.084 bp — still small.** QQQ is liquid enough that 7-figure orders barely move the inside price.
3. **At $10M, impact reaches 0.26 bp.** Now comparable to half-spread (0.72 bp); slippage starts to dominate the cost stack. This is the order of magnitude where capacity becomes the binding constraint, not edge.

For a retail strategy trading $10k–$100k, **explicit cost + half-spread is ~95% of total cost**. Impact bites only in institutional territory.

## §5 — Capacity: where does your own slippage eat the edge?

Capacity is the answer to: **what is the largest Q I can put through this strategy before my own slippage eats the per-trade expectancy?** Set the after-cost expectancy to zero and solve for Q:

> **Formula — strategy capacity Q\*.**
>
> μ<sub>trade</sub> − 2·s − 2·c − 2·η·σ<sub>d</sub>·√(Q\* / ADV) = 0
>
> ⇒ Q\* = ADV · ((μ<sub>trade</sub> − 2s − 2c) / (2η σ<sub>d</sub>))²
>
> where:
> - *μ<sub>trade</sub>* = pre-cost per-trade mean PnL (use bp for everything, or fraction for everything — must be consistent)
> - *s* = half-spread per leg (× 2 for round-trip)
> - *c* = commission per leg (× 2 for round-trip)
> - *η σ<sub>d</sub>* = per-leg impact coefficient (× 2 for round-trip)
> - *Q\** = the *break-even* trade size — at Q\*, after-cost expectancy is exactly zero
>
> If the **impact budget** (μ<sub>trade</sub> − 2s − 2c) is negative, the strategy is unprofitable at any size — costs eat the edge before impact even enters. Then Q\* = $0.

The capacity equation makes spread + commission the **fixed cost** of trading and impact the **variable cost** that grows with size. The fixed cost is paid out of every per-trade dollar; if the fixed cost alone exceeds μ<sub>trade</sub>, there is no room for size.

### Capacity on QQQ at k_σ = 1.0

- μ<sub>trade</sub> (per trade, k=1.0): **+0.317 bp**
- Round-trip explicit cost: 2 · (0.724 + 0.072) = **1.592 bp**
- Impact budget: 0.317 − 1.592 = **−1.275 bp** ← **negative**
- **Capacity Q\* = $0**

The explicit cost wedge (1.59 bp) alone is 5× the per-trade mean (0.32 bp). No clever sizing helps. The capacity is zero.

## §6 — Cost-aware threshold optimization

Maybe `k_σ = 1.0` is the wrong threshold once costs are real. Raising the threshold filters out marginal trades — the ones closest to the noise floor — and keeps the strongest-signal trades. Per-trade mean should rise. Trade count falls (so total PnL might fall too). The right question is: which k_σ maximizes **after-cost** Sharpe?

> **Definition — cost-aware optimization.** Re-tuning a strategy parameter using the after-cost objective function. Different from cost-naive optimization, which optimizes pre-cost and subtracts costs at the end. Cost-aware optima typically sit at higher thresholds and lower trade counts.

### Sweep results

| k_σ | trades | S_pre | S_post |
|---|---|---|---|
| 0.5 | 1519 | +1.28 | −9.44 |
| 0.7 | 1255 | **+2.77** ← cost-naive k\* | −6.40 |
| 1.0 | 892 | +1.48 | −6.09 |
| 1.5 | 485 | +1.28 | −4.16 |
| 2.0 | 263 | +0.09 | −4.36 |
| **2.2** | 200 | +1.18 | **−2.97** ← cost-aware k\* |
| 2.5 | 153 | −0.00 | −3.96 |

**Cost-naive k\* = 0.70 (S_pre = +2.77); cost-aware k\* = 2.20 (S_post = −2.97).**

Two facts to absorb.

1. **The cost-naive optimum (k=0.70) gives the worst after-cost performance.** Low thresholds maximize trade count, and trade count is what costs are levied against. Each marginal trade costs the strategy ~1.6 bp; trades whose pre-cost mean is below that are pure losers post-cost. *The cost-naive choice flips from best to worst once costs are included.*
2. **Even the cost-aware optimum is negative.** S_post = −2.97 at k=2.2, achieved by trading only the most extreme moves (200 trades over the year vs 892 at k=1.0). Raising the threshold concentrates per-trade edge (k=2.2 mean = 0.46 bp vs k=1.0's 0.32 bp) — but not nearly enough to clear the 1.6 bp cost wedge.

The cost-aware optimum is "least bad," not "good." The strategy is unprofitable at every threshold in the sweep.

### Capacity at the cost-aware k\*

At k_σ = 2.20:

- per-trade mean: **+0.461 bp**
- round-trip explicit: 1.592 bp
- impact budget: **−1.131 bp** ← still negative
- **Capacity Q\* = $0**

Raising the threshold to the cost-aware optimum concentrates the per-trade edge from 0.32 bp to 0.46 bp — a 45% gain — but the explicit cost wedge is 1.59 bp regardless. The impact budget moves from −1.27 to −1.13 — closer to zero, still negative. The strategy is structurally dead at any size.

## §7 — The deflation arc, closed by reality

We can now stack every Sharpe quoted for this strategy across Ch8 through Ch12 in order of increasing honesty:

| Stage | Sharpe | What changed |
|---|---|---|
| Ch8 vectorized backtest (in-sample, no costs) | **+2.08** | Overlap + same-bar bug + in-sample |
| Ch9 event-driven (next-open, no costs) | **+0.80** | Honest mechanics; CI straddles 0 |
| Ch10 trailing-σ (bias-corrected, no costs) | **+1.64** | Point-in-time σ |
| Ch10 sweep best (snooped) | +1.86 | Best of 21 — fails Bonferroni |
| Ch11 train/test OOS (no costs) | +0.46 | 30% held out |
| Ch11 walk-forward OOS (no costs) | **+0.88** | 10 monthly refits, CI = (−1.6, +3.5) |
| **Ch12 cost-aware k\*, after-cost** | **−2.97** | Spread (0.72 bp/leg) + commission (0.07) + impact |
| **Ch12 capacity Q\*** | **$0** | Per-trade mean < explicit cost wedge |

The end-to-end deflation: **+2.08 (cost-free, snooped, in-sample) → −2.97 (cost-aware, OOS-honest, after costs)**. A reversal — not a reduction — of sign. The strategy isn't real-but-weak; it isn't even a hypothesis worth more data. **It does not exist as a tradable edge.**

This is what an honest pipeline produces. Most candidate strategies fail at the cost step; the surprise would be if this one didn't.

## So what?

Decision rules this chapter unlocks:

1. **Compute Roll's (or Corwin-Schultz) effective half-spread on your data before *anything* else.** If your strategy's per-trade mean is less than 2× the round-trip spread, you don't have a strategy — you have a cost generator. For a 1-min ETF strategy, the rough bar is per-trade-mean > 2 bp; below that, you're trading the spread of your broker against you.
2. **Re-optimize the threshold parameter under after-cost Sharpe.** Cost-aware optima sit at higher thresholds and lower trade counts. The cost-naive optimum is almost always the *worst* after-cost choice because it maximizes trade frequency, which is what costs are levied against.
3. **Quote capacity Q\* alongside Sharpe.** A strategy that works at $30k may evaporate by $1M. The capacity equation lets you size the lift to a target dollar PnL: at Q\*, after-cost expectancy is zero; halfway up the curve, after-cost expectancy is half its no-impact maximum. Capacity is the link from "strategy works" to "strategy works at the size I need."
4. **If your impact budget is negative, your strategy is dead at any size.** No clever execution trick rescues a negative budget. The right responses: find a strategy with larger per-trade mean (different family, different gate, different instrument with a stickier mispricing); reduce trade frequency; switch to a market with lower bp costs (futures often beat ETFs in bp terms once you account for notional leverage).
5. **Track explicit and implicit cost separately.** Explicit cost is fixed regardless of size; implicit cost grows with √Q. A strategy with a positive impact budget can be sized up until impact catches the budget; one with a negative impact budget cannot be sized at all.

What this chapter cannot yet tell you:

- **Whether limit-order execution beats market-order execution by enough to flip the sign.** Posting passively *captures* half-spread instead of paying it — and on this strategy that swing is roughly 1.4 bp round-trip, comparable to the cost wedge. Ch13 (microstructure & execution) covers this: passive vs aggressive, queue position, partial fills, and the strategy's fill-rate tradeoff.
- **What realized impact actually looks like in production.** η = 0.1 is an empirical average across liquid US equities; on any given day η can swing 2-3×. Ch13 also covers fill-quality measurement (TWAP/VWAP slippage, implementation-shortfall framework).
- **Whether the strategy works on instruments where the cost economics differ.** Exercise 1 below transfers to SPY; Exercise 4 revisits the closing-window Roll's question that motivated this chapter's reframing.

## Key Terms

| Term | Definition |
|---|---|
| Explicit cost | Costs that hit the brokerage statement: commission, exchange/SEC fees, financing. |
| Implicit cost | Costs paid through prices: bid/ask spread (crossed on entry and exit) and slippage / market impact. |
| Half-spread | Half the bid/ask spread; the one-leg cost of crossing the spread once. |
| Roll's estimator | s = √(−Cov(r<sub>t</sub>, r<sub>t−1</sub>)); estimates half-spread from trade-return lag-1 autocovariance. Defined only when cov is negative; gives an upper bound on true spread (genuine MR contaminates). |
| Corwin-Schultz estimator | Estimates spread from two-bar H/L ranges. Independent of Roll's; used as a sanity-check second opinion. |
| Square-root impact law | Empirical regularity: temporary impact = η · σ<sub>d</sub> · √(Q/ADV). η ≈ 0.1 for liquid US equities. |
| ADV (average daily volume) | Typically quoted in dollars; the denominator of the impact equation. Consolidated tape vs venue-specific ADV can differ by ~30×. |
| Strategy capacity (Q\*) | Trade size at which after-cost expectancy crosses zero. Q\* = ADV · ((μ − 2s − 2c) / (2η σ<sub>d</sub>))² when impact budget > 0; Q\* = $0 otherwise. |
| Cost-aware optimization | Re-tuning strategy parameters with after-cost performance as the objective. Yields higher thresholds, lower trade counts than cost-naive. |
| Payment for order flow (PFOF) | Broker routes retail order to a wholesale market maker who pays for the flow. Enables zero commission; shifts cost into the spread the wholesaler captures. |

## Up next

**Ch13 — Microstructure and execution.** Limit-order books, queue position, passive vs aggressive fills, implementation-shortfall measurement. Ch12 priced cost as a fixed wedge; Ch13 turns cost into a function of *how you execute*. A strategy that fails Ch12 with market orders might survive Ch13 with limit orders — at the price of partial fills and slower execution. Whether that survival is genuine or another cost-shifting illusion is the question.

## Exercises

1. **SPY transfer.** Compute Roll's and Corwin-Schultz half-spreads on SPY 1-min (`../06-bridge-to-intraday/data/spy_1min.parquet`). Then re-run the cost-aware k_σ sweep using SPY's own σ<sub>d</sub>, ADV, and Ch7/Ch11's pipeline. Does SPY's after-cost picture look different from QQQ's? *Hint:* SPY's underlying volatility is slightly lower than QQQ's, so per-trade signal-to-noise is smaller; but spread and commission per leg should be comparable.

2. **Cost-sensitivity heatmap.** Build a heatmap with η ∈ {0.05, 0.1, 0.2, 0.3} along one axis and half-spread ∈ {0.5, 1.0, 1.5} bp along the other. Inside each cell, re-optimize k_σ for after-cost Sharpe and store the maximum. Which combinations of η and spread produce *any* positive after-cost Sharpe at all? *Hint:* the cell at (η=0.05, spread=0.5) is the most favorable; if even that doesn't go positive, the strategy is structurally dead.

3. **Capacity vs k_σ.** Plot Q\* against k_σ for k_σ ∈ {0.5, 1.0, 1.5, 2.0, 2.5}. (Use the consolidated ADV $15B; plot Q\* = 0 wherever the impact budget is negative.) Does the cost-aware k\* coincide with the maximum-capacity k\*? If not, the strategy's "optimal threshold" depends on whether your objective is Sharpe or dollar capacity — name the tradeoff.

4. *(Stretch)* **Roll's on subsamples revisited.** §2 found closing-window Roll's *lower* than midday Roll's. Reproduce that, then form the closing-window vs midday Corwin-Schultz comparison. Does CS agree with Roll's on the direction? If both agree closing-window has lower effective spread, what does that say about Ch7's "closing window has 2× MR" finding — is the extra MR genuine signal or partly mechanical?
