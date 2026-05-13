# Chapter 13 — Microstructure and Execution

Ch12 closed the cost cycle on the QQQ closing-window MR strategy with an **after-cost Sharpe of −2.97** at the cost-aware `k_σ*` = 2.20. The spread + commission + impact wedge — about **1.62 bp round-trip** at a $30k notional trade — was several times the per-trade mean PnL (≈ 0.46 bp at `k_σ` = 2.20). The strategy is unprofitable at every threshold; capacity *Q\** = $0.

Ch12 raised one specific rescue hypothesis and closed without testing it: posting **passive limit orders** on entry instead of market orders. A market order *pays* the half-spread; a passive limit, when it fills, *earns* the half-spread. On QQQ that's a swing of about 1.448 bp round-trip — almost the entire cost wedge. If passive entries can be made to fill reliably, the strategy might survive.

This chapter tests that hypothesis honestly. The expected punchline is the canonical microstructure result: **adverse selection eats the spread credit**. Passive limits fill exactly when the market is moving against the posted side, which is precisely when filling is *worst* for the strategy. The chapter measures whether that happens here.

## Three things this chapter covers

1. **Order types are policy choices.** §2. Market vs limit vs marketable-limit vs IOC vs FOK vs hidden vs pegged. Each is a different bet about urgency vs price vs information leakage. Plus the maker/taker rebate structure and what payment-for-order-flow (PFOF) actually buys you.
2. **Passive fills are adversely selected.** §3-§4. A passive entry's Sharpe looks better than a market entry's *before* you condition on whether it filled. After conditioning, the rescue narrows substantially. On this strategy, the *filled-only* drift is +0.29 bp vs the *unconditional* signal-set drift of +0.46 bp — a 0.17 bp toxicity cost. Small here, but the **unfilled** bucket (those signals the limit missed) had +8.1 bp of drift in strategy direction: the strategy's biggest wins are exactly the trades the passive offer self-cancelled.
3. **Latency is an implicit cost.** §5. Signal-to-fill latency × in-window drift = an unbilled cost line. At 1-min bars and 100 ms latency it's 4% of a typical bar's σ (invisible). At 1-sec bars and 200 ms latency it's 45% (dominant). Latency is resolution-dependent.

> **Definition — order type.** A standing instruction to the exchange specifying *when* and *at what price* a buy or sell may execute. Market orders demand immediate execution at any available price; limit orders demand a price floor (or ceiling) at the cost of conditional fill. All the other types refine these two along urgency and visibility axes.
>
> **Definition — maker / taker.** A *taker* removes liquidity from the order book (a crossing market or marketable-limit order). A *maker* adds liquidity (a non-marketable limit order that rests on the book). Exchanges charge takers and pay makers a small per-share rebate; on NASDAQ the tier-1 maker rebate is ~$0.0030/share.
>
> **Definition — adverse selection (toxicity).** The systematic tendency for passive limit fills to occur exactly when the market is about to move against the posted side. Measured as `drift_unconditional − drift_filled`: how much worse a filled passive's post-fill drift is than the strategy's full signal universe.

## §1 — The rescue hypothesis

The Ch12 §2 reframing: Roll's half-spread on QQQ 1-min closes is `s ≈ 0.724 bp`, and Roll's is derived from the *same* lag-1 negative autocovariance that drives Ch7's MR signal. A material chunk of the −0.028 lag-1 ρ in Ch7 is bid-ask bounce, not economic mean-reversion. The strategy was, in part, trying to fade its own counterparty's spread — a structural mismatch, because the strategy must pay the spread to capture the bounce.

The rescue hypothesis flips the sign on the structural mismatch:

- **Buy signal** → post a buy limit at `signal_close − s`. If the limit fills, the entry price is below the signal close by exactly the half-spread; the strategy *receives* `s` instead of paying it.
- **Sell signal** → post a sell limit at `signal_close + s`. Symmetric.

If every signal filled, the round-trip swing would be **+1.448 bp** — almost identical in magnitude to the Ch12 cost wedge that killed the strategy. Combined with rebate income on the maker leg, the rescue looks like it should comfortably flip the sign of the Sharpe.

The chapter tests whether it does.

## §2 — Order types: a short tour

| Order type | What it does | Maker/taker | Fill certainty |
|---|---|---|---|
| **Market** | Buy/sell now at the best available price. | Taker | Near-guaranteed |
| **Limit** | Buy at `≤ p`; sell at `≥ p`. | Maker (if posted away from the touch) | Conditional |
| **Marketable limit** | A limit with price already at-or-through the touch. | Taker (behaves like market with price protection) | Near-guaranteed |
| **IOC (immediate-or-cancel)** | Fill what's available right now; cancel the rest. | Maker on filled portion; nothing rests. | Partial |
| **FOK (fill-or-kill)** | All-or-nothing instant fill; cancel if cannot fill in full. | Maker if filled. | Binary |
| **Hidden** | Limit price + size are not displayed in the public book. Trades at displayed prices but invisible until executed. | Maker. | Conditional, generally lower priority than displayed orders at the same price |
| **Pegged** | Limit price tracks the bid (or offer) at some fixed offset. | Maker. | Conditional |

Each row encodes a different bet:

- **Market vs limit** is the urgency-vs-price tradeoff. You fill *now* and pay the spread, or you fill *if* and earn it.
- **Marketable limit** is a market order with price protection — "fill me now, but never worse than `p`." Useful when the book is thin and you don't want to walk through several levels.
- **IOC / FOK** address what the resting remainder of a partial fill does — IOC cancels it; FOK refuses partial fills entirely. Both prevent the order from leaking your signal by sitting on the book after the moment of trading.
- **Hidden** trades opacity for queue priority (displayed orders fill ahead of hidden orders at the same price).
- **Pegged** automates the "stay one tick off the touch" logic that retail platforms make you do manually.

### Maker / taker economics

Exchanges run a **maker/taker fee model**: a fee for takers (≈ $0.0030/share on most US equity venues) and a smaller rebate for makers (≈ $0.0020-$0.0030/share on tier-1 NASDAQ). The net effect on QQQ at ≈ $695/share is small in bp terms — the rebate alone is **0.043 bp/leg** — but it's not zero, and over a large enough trade count it can be the deciding factor.

### Payment for order flow (PFOF)

When you click "buy" on Schwab or Robinhood as a retail customer, your order is typically *not* routed to the public lit exchange. It is routed to a **wholesale market maker** (Citadel, Virtu, Susquehanna, …) who fills it from inventory at or marginally better than NBBO, in exchange for paying the broker a fraction of a cent per share for the flow.

> **Definition — payment for order flow.** A retail broker routes a customer's order to a wholesaler who fills it at-or-better than NBBO and pays the broker for the right to do so. The price improvement is real (typically 0.01-0.04 bp on a $30k QQQ trade) but the wholesaler keeps the rest of the spread it captures. PFOF makes "zero commission" possible; it shifts the cost into the spread.

PFOF complicates the rescue hypothesis: as a PFOF retail customer, your "market order" is *already* getting some passive-style price improvement vs the lit NBBO. The marginal benefit of switching to your own limit order is smaller than it would be if you were paying full NBBO crossings. The chapter assumes lit-exchange execution (no PFOF) — appropriate for direct-access retail (IBKR) and for any institutional setup.

## §3 — The limit-order simulation

**Fill rule.** A passive entry is posted at the signal bar's close. It fills if a *subsequent* bar within the K-bar hold window prints at-or-through the limit:

- **Buy limit** at `signal_close − s` fills the first time any later bar's `low ≤ signal_close − s`.
- **Sell limit** at `signal_close + s` fills the first time any later bar's `high ≥ signal_close + s`.

If neither condition is met within K bars, the limit *expires unfilled*. Unfilled signals are recorded along with the K-bar post-signal drift in strategy direction — they are the central data for the §4 toxicity diagnostic.

**Exit rule.** Unchanged from Ch12: market-on-open at bar `entry + K`. The exit is still a market order — it pays the half-spread, commission, and impact on the exit leg. (Maker-on-exit is possible but requires abandoning the time stop in favor of a passive-exit limit; that's a Ch16-family decision.)

**Limit-price choice — at-the-touch.** Posting at `signal_close − s` means the buy limit sits *at* the implied bid (the favorable side of the touch). This is the most aggressive passive entry — posting one tick *inside* the touch (a marketable limit) would behave like a market order; posting *outside* the touch by some additional offset δ would lower fill probability but raise per-fill spread credit. The choice δ = 0 (at-the-touch) is the entry-side analogue of Ch12's choice of full-spread cost for market orders — both are the "tightest" parameter in each direction. Exercise 1 sweeps the parameter.

### Two new metrics

| Metric | Definition |
|---|---|
| **Fill rate** | Filled passive trades / total signals. The fraction of would-be market trades that survive as passive trades. |
| **Unfilled count** | Signals where the limit expired. Their post-signal drift (in strategy direction) is the cleanest read on the bias in the unfilled bucket. |

### Empirical result

Running the limit-order backtest at the Ch12 cost-aware `k_σ` = 2.20:

| Quantity | Value |
|---|---:|
| Market signals (baseline; market entries, no costs) | 200 |
| Limit signals | 176 |
| Filled | 157 |
| Unfilled | 19 |
| **Fill rate** | **89.2%** |
| Market-entry mean PnL (pre-cost) | +0.461 bp |
| Filled-only mean PnL (pre-cost, pre-toxicity adjust) | **+0.288 bp** |
| Filled-only annualized Sharpe (pre-cost) | **+0.583** |

Two notes on the numbers:

- **Signal count drops 200 → 176.** The market-order backtest acts on every signal; the limit-order backtest can have at most one trade in flight (in-position or pending) per session, and a signal that arrives while a previous trade is still pending or in position is skipped. This is a realistic constraint for a single-strategy single-account setup.
- **Fill rate is high (89%).** At-the-touch on 1-min bars is aggressive — 1-min bars are wide enough that a subsequent bar's H/L range almost always sweeps through the bid by `s ≈ 0.72 bp`. On finer bars or with a deeper offset, fill rate would drop sharply. The downstream toxicity result is therefore conditional on this fill regime; Exercise 1 explores it.

**First impression — the rescue looks like it works.** Pre-toxicity Sharpe of **+0.58** is a +3.5-point swing from Ch12's after-cost market-order Sharpe of **−2.97**. The strategy appears to be back in business.

§4 explains why this number is a lie.

## §4 — The adverse-selection diagnostic

A passive buy limit posted at the bid fills when sellers cross the spread to hit the bid. Some of those sellers are uninformed (rebalancing, hedging, retail liquidity demand) — their selling is noise; the bid was a good place to provide liquidity. But some are *informed* — they're selling because they know something the passive buyer doesn't, and the price is about to move down. The passive buyer just bought the top of a move down.

This is **adverse selection**. Fills are not a random sample of signals — fills are conditioned on a counterparty being willing to *cross* the spread at that exact moment, and that crossing decision is itself information.

> **Definition — toxicity.** The wedge between unconditional and conditional-on-fill post-event drift, in strategy direction. A measure of how much worse passive fills are than the strategy's full signal universe.

> **Formula — toxicity diagnostic.**
>
> toxicity = drift<sub>unconditional</sub> − drift<sub>filled</sub>
>
> where:
> - drift<sub>unconditional</sub> = mean over all signal bars of the K-bar log-return in strategy direction (= mean PnL of the matched market-order backtest)
> - drift<sub>filled</sub> = mean over filled passive trades of the K-bar log-return in strategy direction (= mean filled-only `pnl_log` from §3)
> - both are in log-return units; multiply by 1e4 for bp
>
> **Sign convention.** Positive toxicity → filled trades did *worse* than the unconditional signal set. The strategy's expectation, computed on signals, overstates what the strategy actually earns.

### Empirical result

| Quantity | Value (bp) |
|---|---:|
| drift<sub>unconditional</sub> (all market-order signals) | +0.461 |
| drift<sub>filled</sub> (limit fills only) | +0.288 |
| **toxicity** | **+0.173** |
| drift on UNFILLED signals (strategy direction) | **+8.106** |

Two findings sit next to each other:

1. **Toxicity is small (+0.17 bp).** By the strict toxicity definition the rescue partly survives. The filled subset is only slightly worse than the unconditional universe; the spread credit isn't fully cancelled by adverse selection on this particular strategy.
2. **The unfilled-bucket drift is enormous (+8.1 bp).** The 19 signals that didn't fill had over 8 bp of drift in strategy direction. **The biggest winners self-cancelled** — when the strategy was most right, the price ran the right way *too fast* for a passive offer at the touch to be hit. The passive entry implicitly filters *out* the strategy's strongest signals.

The asymmetry is the textbook microstructure story in its starkest form. The strict toxicity diagnostic understates it because the unfilled bucket doesn't show up in `drift_filled` at all — but it shows up in *the absence of those trades*.

### Re-pricing the rescue with the rest of the cost stack

The filled-only Sharpe of +0.58 was computed *without* the exit-leg cost stack. The entry leg pays no spread (it's a passive fill — the entry price *is* the better-than-mid execution), but the exit still crosses at next bar's open and pays:

| Exit-leg cost | bp |
|---|---:|
| Half-spread (exit) | 0.724 |
| Commission (round-trip; entry leg pays its half too) | 0.144 |
| Impact at consolidated ADV, $30k notional (round-trip) | 0.029 |

Subtracting the exit-leg-side spread + the full round-trip commission + half the impact from the filled-only PnL:

- **Sharpe (filled-only, post-toxicity, net of exit spread + commission): −1.20**

The +0.58 pre-toxicity Sharpe drops by ~1.8 points once the exit leg pays the wedge that killed Ch12. The "rescue" turns out to be: the *entry* leg's spread becomes a credit; the *exit* leg still pays in full.

## §5 — Latency

> **Definition — signal-to-fill latency.** Wall-clock time between the signal logic emitting an order and the exchange matching engine processing it. Components: signal compute time, network round-trip to broker, broker order routing, exchange matching, response routing back.

Order-of-magnitude reference points:

| Setup | Typical latency |
|---|---|
| Co-located HFT (rack adjacent to matching engine) | < 1 ms (often microseconds) |
| Cloud-hosted retail bot to broker API | 5–50 ms |
| Retail desktop on home internet (Schwab/IBKR API from home) | 50–500 ms |

**Cost framing.** During the latency window the price drifts. If the price drift is independent of the signal (random-walk regime), the standard deviation of the drift scales as √(time):

> **Formula — random-walk latency drift.**
>
> σ<sub>drift</sub> = σ<sub>1min</sub> · √(Δt / 60 s)
>
> where:
> - σ<sub>1min</sub> = per-minute standard deviation of log-returns (QQQ ≈ 4.3 bp)
> - Δt = latency in seconds
> - 60 s = the reference bar duration used to estimate σ<sub>1min</sub>
> - σ<sub>drift</sub> is in the same units as σ<sub>1min</sub> (log-return; multiply by 1e4 for bp)
> - E\|drift\| under a normal model = σ<sub>drift</sub> · √(2/π) ≈ 0.80 σ<sub>drift</sub>

**Two regimes:**

- **Random-walk regime** (signal does not predict directional drift over Δt). The expression above is the cost. For QQQ at 1-min and 100 ms latency: σ<sub>drift</sub> = 4.3 · √(0.1 / 60) ≈ 0.18 bp; E\|drift\| ≈ 0.14 bp. Small relative to a typical 0.72 bp half-spread.
- **Signal-correlated regime** (signal predicts directional drift, as for an MR signal — the price *just* overshot and reversion is expected). The expected cost is the *partial reversion you miss*: ρ · σ<sub>1min</sub> · (Δt / 60 s). With Ch7's lag-1 ρ ≈ −0.028, the expected reversion lost over 100 ms of a 1-min bar is roughly 0.028 · 4.3 · (0.1 / 60) ≈ 0.0002 bp. Truly negligible at 1-min.

The signal-correlated cost is small *because* the latency / bar-duration ratio is tiny at 1-min. As bar resolution shrinks, the ratio grows.

### Latency scenario sweep

| Bar | Latency | σ<sub>drift</sub> (bp) | E\|drift\| (bp) | σ<sub>drift</sub> / σ<sub>bar</sub> |
|---|---:|---:|---:|---:|
| 60 s | 100 ms | 0.176 | 0.140 | 0.041 |
| 60 s | 500 ms | 0.394 | 0.314 | 0.091 |
| 15 s | 200 ms | 0.249 | 0.199 | 0.115 |
| 5 s | 200 ms | 0.249 | 0.199 | 0.200 |
| 1 s | 200 ms | 0.249 | 0.199 | 0.447 |

**Read the rightmost column.** σ<sub>drift</sub> *in absolute bp* depends only on latency (not on bar size — the formula collapses). What changes with bar resolution is the *ratio* to the bar's own σ, i.e., how much of a typical bar move you're losing to latency:

- 1-min / 100 ms: latency drift is **4% of bar σ** — invisible.
- 1-sec / 200 ms: latency drift is **45% of bar σ** — dominant. You're paying half a bar of expected drift on every trade.

**Pedagogical point: latency is a resolution-dependent cost.** Negligible at 1-min, meaningful at 1-sec, dominant at tick. The Ch6/Ch8 choice to work at 1-min bars was implicitly a latency-budget choice: the strategy is robust to retail-grade latency (~100ms) only at 1-min or coarser. A 1-sec or sub-second restatement of the same strategy is unviable on a home internet connection.

## §6 — Maker rebates and the realistic verdict

NASDAQ tier-1 maker rebate ≈ **$0.0030/share** (varies by tier and tape). At QQQ ≈ $694.93/share, that's

> 0.0030 / 694.93 × 1e4 = **0.0432 bp per maker leg**

Small relative to the 0.72 bp half-spread but not zero. The rebate applies to the *entry* leg (the maker side); the exit leg in this chapter is a market order and earns nothing.

Adding the rebate to the post-toxicity filled-only PnL:

- **Sharpe (filled-only, post-toxicity + maker rebate): −1.11**

A +0.09-Sharpe-point improvement from the rebate alone. Real, but small relative to the −1.20 starting point — the rebate is the right size to be a *deciding factor* on strategies that are already near breakeven, and the wrong size to rescue a strategy that's solidly negative.

### The deflation arc, closed

| Stage | Sharpe | Notes |
|---|---:|---|
| Ch8 vectorized in-sample (no costs, snooped) | +2.08 | Ch8 §6 |
| Ch10 trailing-σ (bias-corrected, no costs) | +1.64 | Ch10 §6 |
| Ch11 train/test OOS (no costs) | +0.46 | Ch11 §5 |
| Ch11 walk-forward OOS (no costs) | **+0.88** | Ch11 §7; CI = (−1.6, +3.5) |
| Ch12 cost-aware k\*, market orders, after-cost | **−2.97** | Ch12 §6 |
| **Ch13 passive entry, filled-only, pre-toxicity, pre-cost** | **+0.58** | Apparent rescue |
| **Ch13 passive entry, filled-only, post-toxicity (net exit spread + commission)** | **−1.20** | Actual realized |
| **Ch13 passive entry, filled-only, post-toxicity + maker rebate** | **−1.11** | Final |

**The execution arc:** +0.88 (pre-cost) → −2.97 (market orders) → −1.11 (passive entry, post-toxicity, post-rebate).

Passive execution **narrows the loss by ~1.9 Sharpe points** vs market orders — a real improvement worth quantifying. But the improvement does not cross zero. Two reasons combine to keep it negative:

1. **The exit leg still crosses.** A pure passive *entry* strategy still pays a market-order spread on exit. The half-spread credit gets eaten on the second leg.
2. **The 8.1 bp unfilled-drift means the strategy's biggest winners disappear from the filled ledger.** Even if the round-trip wedge were closed, the filtering bias would cap the rescue's reachable Sharpe well below the no-friction case.

**Decision rule from the arc:** rebates and passive execution matter *when the strategy already has slim-positive expectancy on its own*. They don't rescue a structurally cost-dominated strategy. A different strategy — one with per-trade mean ≥ 3 bp pre-cost, or a strategy where the exit can also be passive — could absorb the cost stack. The Ch7 closing-window MR strategy cannot.

## §7 — So what?

Decision rules this chapter unlocks:

1. **Passive execution is a tool, not a cure.** It helps when (a) the strategy is cost-dominated *and* (b) the signal has low adverse-selection sensitivity *and* (c) both legs can be passive. The Ch7 MR strategy is cost-dominated (a) and has small toxicity (b) on QQQ, but cannot be fully maker/maker because the time-stop exit must cross.
2. **Diagnose toxicity before celebrating the spread credit.** Filled-only conditional drift is the diagnostic; the pre-toxicity Sharpe is the strategy that doesn't exist.
3. **Watch the unfilled bucket.** Strict toxicity (0.17 bp) is one read; the unfilled-signal drift (+8.1 bp) is another, often larger. The passive offer self-cancels the strategy's biggest winners; that's an information-bias cost that does not show up in `drift_filled`.
4. **Match latency to bar resolution.** At 1-min/100ms latency drift is 4% of bar σ; at 1-sec/200ms it's 45%. A 1-sec or sub-second strategy requires co-located or near-co-located execution; a 1-min strategy tolerates retail-grade latency.
5. **Rebates are a tiebreaker, not a strategy.** 0.04 bp/leg flips a marginal-positive strategy across zero; it does nothing for a strategy that's solidly negative after toxicity.

What this chapter *cannot* yet tell you:

- **Given an honest after-execution expectancy and confidence interval, how much capital to deploy per trade?** Ch14 (position sizing, Kelly, risk of ruin) closes that loop. Spoiler: when after-execution expectancy is negative, Kelly says zero — the framework matters for the next strategy.
- **Whether the same execution analysis applies to other strategy families.** Ch16 revisits: momentum *wants* to take (the signal is the move that's coming, and being early earns more than the spread saves); MR *wants* to make (theoretically) but is compromised by exactly the adverse-selection / unfilled-bucket bias surfaced here; breakout is mixed (front-running vs confirming the break).
- **What futures microstructure looks like.** Ch17-18 — the toxicity / fill-rate / latency framework all carries over, but the CME order book, tick size economics, and futures-specific fee structures change the magnitudes substantially.

## Key Terms

| Term | Definition |
|---|---|
| Market order | Order to execute immediately at the best available price. Taker side; pays the spread. |
| Limit order | Order to execute only at price *p* or better. Maker side (if posted away from the touch); conditional fill. |
| IOC (immediate-or-cancel) | Limit that fills whatever can fill now and cancels any remaining size. Prevents resting leakage. |
| FOK (fill-or-kill) | Limit that fills in full immediately or cancels entirely. |
| Maker | Liquidity-providing side; posts a non-marketable limit that rests on the book; earns the maker rebate. |
| Taker | Liquidity-removing side; crosses the spread with a market or marketable limit; pays the taker fee. |
| Payment for order flow (PFOF) | Routing of retail orders to wholesale market makers in exchange for payment to the broker; enables zero-commission retail. |
| Fill rate | Filled passive trades / total signals. The fraction of would-be market trades that survive as passive trades. |
| Adverse selection / toxicity | The systematic tendency for passive fills to occur when the market is about to move against the posted side. Quantified as `drift_unconditional − drift_filled`. |
| Latency | Wall-clock time from signal emission to exchange match. Random-walk component scales as σ<sub>1min</sub> · √(Δt / 60 s). |
| Maker rebate | Per-share credit paid by the exchange to the maker (passive liquidity provider). NASDAQ tier-1 ≈ $0.0030/share ≈ 0.043 bp/leg on QQQ at $695. |

## Up next

**Ch14 — Position sizing and risk of ruin.** With the after-execution expectancy in hand (here: negative), Kelly tells us how much capital to deploy per trade. The Kelly fraction is a function of the post-execution edge and the per-trade variance — using the pre-cost Sharpe of +0.88 would have us deploying meaningful capital on a strategy that loses money in practice. The Ch12-Ch13 deflation chain is the input that makes Ch14 honest.

## Exercises

1. **Fill-rule strictness.** Re-run the §3 backtest under three fill rules:
   (a) any later bar within K touches the limit (used in the chapter),
   (b) only the *next bar's open* may touch,
   (c) a bar must *trade through* the limit by ε ticks ($0.01 say).
   Compute fill rate, drift_filled, and toxicity under each. Does the +0.17 bp toxicity result survive rule (c)? Which rule is the most realistic for a retail simulator, and why?

2. **Latency sensitivity sweep.** For QQQ at 1-min, 15-sec (resampled), and 5-sec resolutions, compute σ<sub>drift</sub> and E\|drift\| under 100 ms and 500 ms latency assumptions. At what bar resolution does the latency drift exceed the 0.72 bp half-spread credit? *Hint:* you don't need new data; σ<sub>1min</sub> and the √(Δt/60) formula are sufficient.

3. **Maker-rebate breakeven.** Hold fill rate (0.89) and toxicity (0.17 bp) constant. What per-trade gross PnL (in bp) would the strategy need before the 0.043 bp/leg maker rebate is the *deciding* factor between losing and breaking even on after-cost Sharpe? Express the answer in terms of fill rate, gross per-trade std, and the exit-leg cost stack from Ch12.
