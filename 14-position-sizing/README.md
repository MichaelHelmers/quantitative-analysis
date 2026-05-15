# Chapter 14 — Position Sizing and Risk of Ruin

Ch13 closed the execution arc on the QQQ closing-window MR strategy at **after-cost, post-toxicity, post-rebate Sharpe of −1.11**. The strategy is unprofitable in production. For a position-sizing chapter, that is awkward: the textbook Kelly fraction on a negative-edge strategy is **zero**, and "bet nothing" is not a chapter.

So this chapter stipulates a positive-EV (positive *expected value* — μ > 0 in returns) synthetic strategy — a cousin of the Ch7-Ch13 strategy, sharing its per-trade σ but with a small positive μ — and uses it to exercise every sizing rule. The numbers in this chapter are **not** a backtest of the real strategy. They are the cleanest possible numerical fixture: closed-form Kelly, closed-form vol target, a tractable Monte-Carlo for drawdown, a tractable GPD fit for tails. Ch16 hunts for a real positive-EV candidate; until then, the stipulated cousin is a teaching fixture.

> **Honest disclaimer.** The annualized Sharpe of the stipulated strategy is **5.56** — *unrealistically high by design*. The chapter wants sizing rules to bite via leverage choice, not be obscured by signal noise. Do not benchmark real strategies against the stipulated numbers in this chapter.

## Three things this chapter covers

1. **Kelly is a noise diagnostic on bp-scale strategies (where per-trade returns are measured in basis points — 1 bp = 0.01% = 1e-4), not a sizing rule.** §2. The textbook fraction μ/σ² evaluates to **204× equity** on the stipulated strategy. The textbook's own derivation (Taylor-expand log(1 + f·r) and assume |f·r| ≪ 1) does not support that number. The right diagnostic is **f·σ**, the per-trade equity-at-risk per σ of return; when it is not ≪ 1, Kelly is informational, not prescriptive.
2. **Drawdown stops are regime-change detectors, not free risk reduction.** §5. On a stationary positive-EV strategy with a known DGP (data-generating process — the joint distribution producing each trade's return), halve-on-5% and halt-on-10% are both strictly suboptimal in expected growth. They earn their keep when the DGP changes; that is a Ch15 conversation, not a Ch14 one.
3. **EVT extrapolates beyond what you have observed.** §6. Empirical Monte-Carlo says nothing about tail events that have not yet occurred in your simulation. A Generalized Pareto fit to per-trade losses (peaks-over-threshold) gives you a shape parameter ξ̂ that tells you which tail-domain you are in. The Normal-vs-Student-t comparison shows ξ̂ flipping sign across two distributions with the same variance — the warning sign EVT is designed to catch.

The chapter's recommended baseline rule is **vol targeting** at τ<sub>daily</sub> ≈ 1%. Median max drawdown (MDD — the largest peak-to-trough equity decline observed over a path) stays under 6%, p95 MDD under 10%, and the realized Sharpe is within 2% of the unit-notional Sharpe.

> **Definition — position size.** The notional amount (or fraction of equity) committed to a single trade. Distinct from leverage, which is the ratio of total notional exposure to equity across all open positions.
>
> **Definition — leverage.** Total exposed notional divided by equity. A leverage multiplier of 5× means $5 of notional position per $1 of equity. Leverage > 1 requires borrowing (margin) or a derivative that synthesizes it (futures, swaps).
>
> **Definition — log-wealth growth rate.** The expected change in log-equity per period: g = E[log(W<sub>t+1</sub>/W<sub>t</sub>)]. Maximizing g maximizes the long-run geometric growth of wealth — the right objective for a strategy compounding its own capital. Distinct from maximizing E[W<sub>t+1</sub>] (the arithmetic mean), which can be made arbitrarily large by piling on leverage at the cost of certain ruin.

## §1 — The stipulated strategy

The chapter operates on a stipulated cousin of the Ch7-Ch13 strategy. The cousin shares the per-trade σ but is given a small positive per-trade μ, so the sizing math has something to optimize against:

| Parameter | Value | Source |
|---|---:|---|
| Per-trade mean μ | **1 bp** = 1e-4 | Stipulated. Realistic order of magnitude for a marginal MR signal (Ch11 walk-forward put real μ ≈ 0.2-0.5 bp, here we round up). |
| Per-trade std σ | **7 bp** = 7e-4 | Matches Ch11/Ch12's measured per-trade σ on the closing-window strategy. |
| Trades per session | **6** | Chosen so daily σ ≈ 17 bp matches QQQ daily realized vol order of magnitude. |
| Sessions per year | **252** | US trading calendar (Ch1 §2). |
| Returns | i.i.d. (independent and identically distributed) N(μ, σ²) | The "easy case." Real returns are not i.i.d. and not Normal; the Ch15 vol-targeting refinement and the §6 EVT sidebar both relax this. |

Derived statistics:

- **Per-trade Sharpe** = μ/σ = 1e-4 / 7e-4 ≈ **0.143**.
- **Annualized Sharpe** = per-trade Sharpe · √(trades/year) = 0.143 · √(6·252) ≈ **5.56**.

The annualized number is *not* a target. It is a teaching fixture: the chapter wants sizing rules to differ visibly under MC, and a small-Sharpe synthetic would have those differences buried in noise. Real strategies that compound at Sharpe ≈ 5 do not exist outside a handful of HFT shops; treat the 5.56 as a control variable, not a benchmark.

### The three operational questions

Once you have a positive-EV strategy you need to answer three sizing questions, in order:

1. **Per-trade.** What fraction f of equity to commit per signal? §2 (Kelly), §3 (fixed-fractional / fixed-dollar).
2. **Per-period.** What target portfolio volatility τ<sub>daily</sub> to run at? §4 (vol targeting).
3. **When to stop.** What drawdown triggers reduced or zero sizing? §5 (drawdown stops), §6 (risk-of-ruin extrapolation).

Each question has a textbook answer that mostly works at small bet sizes. The chapter's main pedagogical job is to show *where the textbook answers break* on bp-scale returns.

## §2 — Kelly

The Kelly criterion picks the bet size that maximizes long-run log-wealth growth. Two forms appear in the literature.

### Bernoulli form

For a binary bet that wins $b per $1 risked with probability p and loses $1 with probability q = 1 − p:

> **Formula — Bernoulli Kelly.**
>
> f\* = (bp − q) / b
>
> where:
> - f\* = fraction of equity to bet on the next round
> - b = win:loss payoff ratio (e.g., b = 1 for an even-money bet, b = 2 for 2:1)
> - p = probability of winning the bet
> - q = 1 − p = probability of losing

Plain English: f\* is **edge over odds**. The numerator (bp − q) is the bet's expected return per $1 risked (the edge); the denominator b normalizes by the payoff ratio. This is the same edge/expectancy quantity that drove Ch7 §1's expectancy framing — Bernoulli Kelly is the bet-sizing translation of that expectancy.

### Continuous form

For a strategy with per-trade return r ~ N(μ, σ²):

> **Formula — Continuous (log-normal) Kelly.**
>
> f\* = μ / σ²,    g\* = ½ · μ² / σ²
>
> where:
> - f\* = fraction of equity allocated per trade (a *leverage multiplier* when f\* > 1)
> - μ = per-trade expected return (in decimal, not bp)
> - σ² = per-trade return variance (in decimal²)
> - g\* = expected log-wealth growth rate per trade *at the optimal fraction f\**
> - r = the realized per-trade return random variable

<details>
<summary>Derivation (second-order Taylor expansion of log)</summary>

Wealth after one trade at fraction f is W<sub>1</sub> = W<sub>0</sub>·(1 + f·r). The log-wealth growth per trade is

> log(W<sub>1</sub>/W<sub>0</sub>) = log(1 + f·r)

For small |f·r|, the second-order Taylor expansion of log(1 + x) ≈ x − ½·x² gives

> log(1 + f·r) ≈ f·r − ½·(f·r)²

Taking the expectation under r ~ N(μ, σ²):

> E[log(1 + f·r)] ≈ f·μ − ½·f²·E[r²] = f·μ − ½·f²·(σ² + μ²) ≈ f·μ − ½·f²·σ²

where the last step drops the μ² term as negligible relative to σ² for small μ (the bp-scale assumption).

Differentiating with respect to f and setting to zero:

> d/df [f·μ − ½·f²·σ²] = μ − f·σ² = 0    ⇒    **f\* = μ/σ²**

Substituting back:

> **g\* = ½ · μ²/σ²**

This is the per-trade log-wealth growth rate at the Kelly-optimal fraction.

**Critical caveat.** The Taylor expansion is only valid when |f·r| ≪ 1. The formula gives an answer regardless; whether you should *use* that answer depends on whether the small-bet assumption holds. The next subsection shows it does not on bp-scale strategies.
</details>

### Worked numbers on the stipulated strategy

Plugging μ = 1e-4 and σ = 7e-4 into f\* = μ/σ²:

> **f\* = 1e-4 / (7e-4)² = 1e-4 / 4.9e-7 ≈ 204.08**

This is not "2% of equity." It is **20,408% of equity** — about 204× leverage per trade. The textbook formula is telling you to borrow 203 dollars for every dollar of capital and bet all 204 of them on the next trade.

The per-trade growth rate at f\* is

> g\* = ½ · (1e-4)² / (7e-4)² ≈ 1.02e-2 per trade

which annualizes to roughly 15.4 log-units per year — about 5·10⁸ percent total return. **At the cost of certain ruin if any input is mis-estimated.**

### The unit-sensitivity gotcha (CC-1)

The right diagnostic on a bp-scale strategy is **not f\* alone but f\*·σ** — the per-trade equity-at-risk per standard deviation of return:

> **Diagnostic — f·σ (equity-at-risk per σ).**
>
> At full-Kelly on the stipulated strategy:
> - f\* · σ = 204.08 · 7e-4 ≈ **0.143**
> - A **1σ adverse move** vaporizes f·σ ≈ **14.3%** of equity
> - A **3σ adverse move** vaporizes 3·f·σ ≈ **42.9%** of equity

The Kelly derivation assumes |f·r| ≪ 1. With f·σ ≈ 0.14 and r occasionally reaching ±3σ, |f·r| is routinely ~0.4 — not ≪ 1. **The textbook formula has already left its zone of validity.** It returns a number that the derivation itself does not support.

This is the chapter's CC-1 finding: on bp-scale returns the textbook Kelly fraction is over-levered by orders of magnitude, *and the derivation does not catch the breakdown automatically*. You have to check f·σ by hand. If f·σ is not ≪ 1 (say, > 0.02), Kelly is informational at best.

### Why under-bet? Four reasons

The literature lists three classical reasons to bet a fraction k·f\* with k < 1. This chapter adds a fourth.

1. **μ is estimated.** The standard error on μ̂ from N i.i.d. trades is σ/√N. With N = 1,500 trades (a year of the stipulated strategy at 6/session) and σ = 7 bp, SE(μ̂) ≈ 1.81e-5 — about 18% of μ itself. A +1-SE optimistic μ̂ inflates f\* by ~18%; a +2-SE optimistic μ̂ inflates by ~36%, with a ~13% growth penalty when evaluated under the true μ. Exercise 1 works this out.
2. **Fat tails.** Kelly's Taylor expansion assumes well-behaved σ². Under fat-tailed r the second-order approximation under-states downside, which means the textbook f\* over-states the safe bet. The §6 sidebar and Exercise 3 measure how badly.
3. **Max-DD pain.** Thorp's classical result on full-Kelly under continuous trading: the maximum drawdown over an infinite horizon distributes as P(max DD ≥ x) = 1 − x for x ∈ [0, 1], so a 90% drawdown has 10% lifetime probability. Few humans tolerate that even if they trust the math.
4. **Unit sensitivity (this chapter).** On bp-scale returns f\*·σ is not ≪ 1, and the formula's own derivation breaks down. The right response is to cap leverage at quarter-Kelly or below and treat Kelly as a sanity ceiling, not a sizing rule.

### Growth-rate-vs-leverage curve

Substituting f = k·f\* into g(f) = f·μ − ½·f²·σ² gives

> **g(k·f\*) = k · f\* · μ − ½ · (k·f\*)² · σ²**

which is a parabola in the leverage multiplier k:

- Peaks at **k = 1** (full-Kelly), with value g\*.
- Zeros at **k = 0** (don't bet, no growth) and **k = 2** (over-bet, growth eaten by variance drag).
- **Negative for k > 2**: bet more than twice Kelly and your expected log-wealth shrinks per trade.

The peak is flat. Half-Kelly (k = 0.5) gives 75% of peak growth at half the leverage; quarter-Kelly gives 44% of peak growth at one-quarter the leverage. *What this means for the next position you take*: most of the growth lives in the first half-step toward Kelly; the second half buys very little additional growth at the cost of much larger drawdowns. **Stop at half or quarter; never go past one.**

### Half-Kelly and quarter-Kelly under the unit-sensitivity lens

The standard practitioner advice — "Half-Kelly is the practical sweet spot" — was developed on Bernoulli-like bets where f\* lands in the 10-30% range and bets are bounded. On the stipulated strategy:

| Rule | f | f·σ | 1σ-loss | 3σ-loss |
|---|---:|---:|---:|---:|
| Full Kelly | 204.08 | 0.1429 | 14.3% | 42.9% |
| Half Kelly | 102.04 | 0.0714 | 7.1% | 21.4% |
| Quarter Kelly | 51.02 | 0.0357 | 3.6% | 10.7% |

Quarter-Kelly's f·σ ≈ 0.036 is still 1.8× the "safe" threshold of 0.02. Empirically, quarter-Kelly's p95 max DD on this strategy is **60%** (see §7). Half-Kelly's p95 max DD is **87%** — within a hair of ruin.

**The honest recommendation:** use Kelly as a sanity ceiling. Cap leverage at quarter-Kelly or below, and pick the actual operating size by vol targeting (§4), which removes μ from the formula entirely.

## §3 — Fixed-fractional and fixed-dollar

Two simpler rules from the retail trading literature.

### Fixed-fractional

The retail-textbook default: "never risk more than r<sub>per_trade</sub> = 2% of equity per trade." Operationalized:

> **Formula — Fixed-fractional sizing.**
>
> size = (r<sub>per_trade</sub> · equity) / d
>
> where:
> - size = position size as a fraction of equity (a leverage multiplier when > 1)
> - r<sub>per_trade</sub> = the fraction of equity you are willing to lose per trade (e.g., 0.02 for "2% rule")
> - d = stop distance in return units (the distance from entry to your stop-loss, expressed as a fractional move)
> - equity = current account equity

**How it differs from Kelly.** Fixed-fractional ignores μ entirely. It sizes purely off downside (the stop distance d), bets equal *risk* per trade, and is invariant to your estimate of the edge. Kelly, by contrast, sizes off μ/σ² — it bets equal *edge per unit of variance*. When d is roughly constant across trades, fixed-fractional and Kelly are linearly related; when d varies (variable signal strength), they diverge.

### Worked number

On the stipulated strategy with r<sub>per_trade</sub> = 2% and d = σ<sub>trade</sub> = 7 bp (a 1σ-per-trade stop):

> size = 0.02 / 0.0007 ≈ **28.6×** equity

Still over-levered. **Why?** A 1σ-per-trade stop is too tight relative to the strategy's holding horizon. With 6 trades per session and i.i.d. returns, the position is exposed to 6 draws of σ across a session, so a session-scale stop is the more honest reference:

> d = σ<sub>daily</sub> = σ · √6 ≈ 17.15 bp = 0.001715
> size = 0.02 / 0.001715 ≈ **11.7×**

Still high. The lesson from the bp-scale unit-sensitivity gotcha (§2) repeats here in a different form: **the stop distance must be commensurate with the holding horizon, not the per-bar σ.** If you mis-scale d, fixed-fractional over-levers exactly the way Kelly does.

### Fixed-dollar

Constant notional per trade: size = $N regardless of equity, σ, or signal strength. The honest baseline.

- **Does not compound.** Doubling equity does not double the next position; growth is linear, not geometric.
- **Does not adapt to drawdowns.** A 50% drawdown leaves the next trade at the same notional, which is now twice the *fractional* size — exactly the wrong direction.
- **Useful when you don't trust your μ̂ / σ̂ estimates.** Institutions running a new strategy often start fixed-dollar, log realized μ and σ for a few months, then graduate to vol targeting (§4) once σ̂ is stable. The fixed-dollar phase is risk-managed by capping $N at a level where total drawdown can be absorbed by the rest of the book.

### Comparison narrative

| Rule | Sizes off | Compounds? | Adapts to signal strength? |
|---|---|---|---|
| Fixed-dollar | Nothing (constant $N) | No | No |
| Fixed-fractional | Stop distance d, equity | Yes | Only via d |
| Kelly | μ, σ² | Yes (geometrically optimal in theory) | Yes |
| Vol target (§4) | σ̂, target τ | Yes | Yes (via σ̂) |

When stop distance d is roughly constant across trades, fixed-fractional ≈ Kelly up to a constant. When d varies — i.e., when the strategy reads off variable signal strength and picks d to match — fixed-fractional bets equal *risk*, Kelly bets equal *edge/risk²*. Different rules; same family.

## §4 — Vol targeting (the chapter's recommended baseline)

The institutional standard: set leverage so that the *expected per-period PnL volatility* equals a stated target. The target is the knob; everything else is derived.

> **Formula — Vol-targeted size.**
>
> size<sub>t</sub> = (τ<sub>daily</sub> · equity) / σ̂<sub>t</sub>
>
> where:
> - size<sub>t</sub> = position size (in equity units) for period t — a leverage multiplier when > 1
> - τ<sub>daily</sub> = target per-day return standard deviation (e.g., 0.01 for "1% daily vol target")
> - σ̂<sub>t</sub> = forecast per-day standard deviation of position PnL at unit notional, going into period t
> - equity = current account equity
>
> The ratio τ<sub>daily</sub> / σ̂<sub>t</sub> is the leverage multiplier.

### Worked number

On the stipulated strategy, daily PnL σ at unit notional is

> σ<sub>daily</sub> = σ<sub>trade</sub> · √(trades per session) = 7 bp · √6 ≈ **17.15 bp** = 0.001715

At τ<sub>daily</sub> = 1%:

> leverage = 0.01 / 0.001715 ≈ **5.83×**

This is two orders of magnitude below full-Kelly's 204× and one order below the fixed-fractional 2%/1σ-stop 28.6×. It is also the only operating point on the stipulated strategy where median MDD is < 6% and p95 MDD is < 10% — see §7.

### Choice of σ̂<sub>t</sub>

The chapter uses a **rolling 20-day realized standard deviation** as σ̂<sub>t</sub>. This is the cheapest defensible estimator: it makes no assumption about the σ-process beyond local stationarity, and it adapts (slowly) to regime change.

**Forward-pointer to Ch15.** σ̂<sub>t</sub> is the chapter's biggest unmodeled assumption. Ch15 sharpens it in three ways: (i) GARCH-style updating to capture vol clustering (Ch2 found QQQ has strong vol autocorrelation), (ii) intraday seasonality (vol is higher at the open and close), (iii) regime detection (a σ̂<sub>t</sub> that knows when to fast-update). All three plug into the same formula above; they refine the input, not the rule.

### Regime sensitivity

Vol targeting is correct *given* σ̂<sub>t</sub>. When σ̂<sub>t</sub> lags true σ, you are mis-levered:

> If true σ doubles while σ̂<sub>t</sub> hasn't yet updated, realized leverage is **double the target** during the lag window.

The chapter's 20-day rolling σ̂<sub>t</sub> lags a step change in true σ by roughly 10-15 sessions before catching up. Exercise 2 demonstrates this and measures the over-leveraged window's drawdown.

### Relation to Kelly

Vol targeting is **"Kelly with a stipulated leverage budget instead of a derived one."** The two reconcile when the operator picks τ<sub>daily</sub> such that

> τ<sub>daily</sub> / σ̂<sub>daily</sub> = f\*

On the stipulated strategy, full-Kelly leverage is 204× and unit-notional daily σ is 17.15 bp, so the matched τ<sub>daily</sub> would be 204 · 0.001715 ≈ 35%/day. **Nobody runs at 35% daily vol.** Vol targeting recovers sanity by dropping μ from the formula entirely — μ is the noisiest input — and letting the operator pick the volatility budget directly.

This is the chapter's chosen baseline rule.

## §5 — Drawdown control

Drawdown stops are sizing rules conditioned on path: scale the bet down when the running drawdown gets too large.

### Reading the §5 fan charts

The notebook's §5 panel shows p5 / p50 / p95 equity-vs-time across 10,000 MC paths under each sizing rule (drawdown machinery from Ch5 §2). Read these as **bands** — each band shows where 90% of paths land at each time:

- **Unit notional** sits in a narrow band centered just above 1. No leverage, no drama; median final wealth ≈ 1.16, p95 MDD ≈ 1.6%.
- **Full Kelly**'s *mean* final is ~10¹², dominated by a handful of lottery-winner paths; the p50 equity path is near-zero (median MDD 95.9%) and the p5 path ends at **0.04**. The fan looks "good" only if you average; if you read the median (the typical path), you go bankrupt.
- **Vol target (5.83×)** is a tight band. Median MDD ≈ 5.9%, p95 MDD ≈ 9.2%.
- **Fixed-fractional 2%** is a wide fan but bounded; p95 MDD ≈ 39%.

The fan-chart geometry maps directly to the bet-size geometry: more leverage means a wider band, with the upper tail growing faster than the lower tail is bounded.

### Drawdown-stop rules

Two variants on the Half-Kelly base:

> **Definition — halve-on-5% DD.** If running drawdown from trailing equity peak ≥ 5%, multiply position sizes by 0.5. Restore full sizing when equity recovers to within 2% of the prior peak.
>
> **Definition — halt-on-10% DD.** If running drawdown from trailing equity peak ≥ 10%, set position size to 0 (stop trading entirely). In this variant, no re-entry condition — once halted, halted permanently.

The halve rule is a *gradual* sizing reduction; the halt rule is *binary*. The halt variant deliberately omits a re-entry trigger because the chapter wants to measure the cost of being wrong about when to restart.

### The honest empirical finding (CC-2)

On a **stationary, known-positive-EV strategy**, drawdown stops are strictly suboptimal. Numbers on the Half-Kelly base (full 9-row table in §7):

| Rule (10,000 MC paths) | Mean final | p95 MDD |
|---|---:|---:|
| Half Kelly | 4,400,562 | 87.5% |
| Half-Kelly + halve-on-5% | 12,207 | 62.5% |
| Half-Kelly + halt-on-10% | 1.11 | 17.3% |

- **Halve-on-5%** cuts mean final by **361×** in exchange for a 29% relative reduction in p95 MDD.
- **Halt-on-10%** cuts mean final from 4.4M to **1.11** — compounding is killed entirely, because the variant has no re-entry — in exchange for an 80% reduction in p95 MDD.

The arithmetic is brutal: on a stationary positive-EV strategy, the expectation drags equity back up after a drawdown. Stopping during the drawdown cuts you off from the recovery. The strategy "wants" to recover; the stop prevents it.

### Reframe — what stops are actually for

Stops are **regime-change detectors**, not free risk reduction. Their job on a stationary i.i.d. positive-EV strategy is to limit psychological / institutional pain, not to improve expected growth. The right reason to halt is **"the strategy has stopped working"** — i.e., the DGP has changed. On a stipulated stationary strategy where the DGP is *known* to be positive-EV, every halt is wrong.

The honest behavioral caveat: drawdown stops are a **utility-function** control, not a **growth-rate** tool. Whether to use them is a question about your tolerance for staring at a 50% drawdown — yours or your investors' — not a question about expectation. Real strategies are non-stationary (Ch2 showed QQQ vol clusters; macro regimes shift; signals decay). Stops do earn their keep when regimes change. But that detection is a Ch15 conversation, not a Ch14 one. **Don't generalize the "stops are bad" finding to non-stationary strategies.**

## §6 — EVT sidebar: tail shape and risk-of-ruin

How likely is a max drawdown of, say, 20% over a year on the stipulated strategy? Two approaches.

### Approach 1 — empirical Monte Carlo

Run 10,000 paths under your chosen sizing rule and count the fraction with max DD ≥ 20%. Direct, model-free, intuitive. The catch: at *very deep* DD thresholds (40%, 50%) the empirical count gets noisy fast. To say "P(DD ≥ 50%) = 0.001" you need at least ~10 paths breaching 50%, which means ~10,000 paths to get the count and ~100,000 to get the count to within 30% relative error.

### Approach 2 — EVT via the Generalized Pareto Distribution

Fit a Generalized Pareto Distribution (GPD) to per-trade losses exceeding a high threshold u (peaks-over-threshold, POT). This is the EVT preview that retired-Ch10 left for §6 (Ch10 §EVT).

> **Formula — GPD density (peaks-over-threshold).**
>
> f(x; ξ, σ<sub>GPD</sub>) = (1/σ<sub>GPD</sub>) · (1 + ξ · x / σ<sub>GPD</sub>)<sup>−1/ξ − 1</sup>
>
> for x ≥ 0 (where x is the *excess* over threshold u: x = r − u for losses r > u)
>
> where:
> - x = excess loss magnitude over threshold u (so x ≥ 0)
> - u = chosen threshold (typically a high quantile of the loss distribution; this chapter uses the 95th percentile)
> - ξ = **shape parameter** — the tail-domain indicator
>   - ξ > 0: heavy tail (Fréchet domain) — Pareto-like, power-law decay, **unbounded worst case**
>   - ξ = 0: exponential tail (Gumbel domain) — moments exist at all orders
>   - ξ < 0: bounded tail (Weibull domain) — there is a finite worst possible loss
> - σ<sub>GPD</sub> = scale parameter — controls the spread of excesses (analogous to σ in a Normal but for the tail only)

The shape ξ is the headline. It tells you *which kind* of distribution generated your tail, independent of the bulk. Two distributions with identical mean and variance can have wildly different ξ, and ξ is exactly what governs worst-case behavior.

### Honest scoping (CC-3)

EVT on per-trade losses does **not** directly predict max-DD — max-DD is a *path functional* of the trade sequence (max over t of (peak − equity<sub>t</sub>) / peak), while GPD is fitted to single-period loss magnitudes. The two are connected but not equivalent.

A more pointed problem: under full-Kelly leverage on the stipulated strategy, MC P(DD ≥ X) saturates at 1.0 for every X ≥ 10% — every path eventually breaches every threshold. The MC-vs-EVT comparison is degenerate at that leverage. **The chapter runs the comparison at the recommended vol-target leverage 5.83× instead**, where MC has signal and the comparison can teach.

### Headline finding

On i.i.d. Normal per-trade returns (the stipulated DGP), fitting GPD to the lower-tail excesses at threshold u = 95th-percentile loss:

> **ξ̂ = −0.120, σ̂<sub>GPD</sub> = 3.28e-4**

ξ̂ < 0 → **bounded tail in the Weibull domain**, as expected from a Normal (Normal has all moments finite and its tail decays faster than exponential).

At vol-target 5.83× leverage:

| Quantity | Value |
|---|---:|
| MC P(DD ≥ 10% \| vol-target) | 0.0292 |
| MC P(DD ≥ 20% \| vol-target) | 0.0000 |
| MC P(DD ≥ 30% \| vol-target) | 0.0000 |
| POT 99.9-th-percentile single-trade loss (Normal) | 20.7 bp |
| Single-trade equity hit at vol-target leverage | **1.21% of equity** |

A 1.21% single-trade equity hit is well inside any 10% MDD bound. EVT and MC agree at this leverage: tail risk is bounded and manageable.

### The fat-tail story — same variance, different ξ

Refit GPD on Student-t(df=4) returns with matched variance to the Normal case:

> **ξ̂<sub>t</sub> = +0.192, σ̂<sub>GPD,t</sub> = 4.28e-4**

A **sign flip into the Fréchet (heavy-tail) domain.** Same μ, same σ, fundamentally different tail behavior:

- Normal (ξ̂ = −0.12): bounded worst case; expected-shortfall at threshold X stops growing as X → tail boundary.
- Student-t(df=4) (ξ̂ = +0.19): unbounded worst case; expected-shortfall grows with the threshold; arbitrarily large losses have non-negligible probability.

At vol-target 5.83× leverage, MC P(DD ≥ 10%) is 0.029 for Normal vs ~0.036 for Student-t — small absolute gap. The gap **grows with leverage** and with the DD threshold; Exercise 3 walks through it for P(DD ≥ 30%) and P(DD ≥ 50%).

**The pedagogical point.** EVT is the right tool when you want to extrapolate beyond what you have observed. Empirical MC at 10,000 paths cannot reliably say "P(DD ≥ 50%) is 0.0003 vs 0.003" because you would not see enough breaches at either rate. GPD's ξ̂ on the *observed* per-trade losses tells you which world you are in — bounded or unbounded — and that knowledge propagates to tail probabilities you have not yet sampled. **Pay for the insurance whether or not your tails turn out to be fat.**

## §7 — Side-by-side

Final 9-row comparison across all rules considered (10,000 MC paths, 1,512 trades per path = 252 sessions × 6 trades/session, i.i.d. N(μ, σ²) draws):

| Rule | Mean final | Median MDD | p95 MDD | P(DD ≥ 20%) | P(DD ≥ 50%) | Mean Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| Unit notional | 1.16 | 1.0% | 1.6% | 0.000 | 0.000 | 5.53 |
| Full Kelly | 1.96 × 10¹² | 95.9% | 99.6% | 1.000 | 1.000 | 2.73 |
| Half Kelly | 4,400,562 | 71.7% | 87.5% | 1.000 | 0.996 | 4.17 |
| Quarter Kelly | 2,163 | 43.6% | 60.4% | 1.000 | 0.247 | 4.86 |
| Fixed-fractional 2% | 74.0 | 26.5% | 38.9% | 0.920 | 0.003 | 5.17 |
| Vol-target τ<sub>daily</sub>=0.63% (3.67×) | 1.74 | 3.7% | 5.9% | 0.000 | 0.000 | 5.50 |
| **Vol-target τ<sub>daily</sub>=1.0% (5.83×)** | **2.41** | **5.9%** | **9.2%** | **0.000** | **0.000** | **5.47** |
| Half-Kelly + halve-on-5% | 12,207 | 46.7% | 62.5% | 1.000 | 0.349 | 4.41 |
| Half-Kelly + halt-on-10% | 1.11 | 11.9% | 17.3% | 0.015 | 0.000 | 0.02 |

**Read this table by median MDD, not mean final.** Kelly's mean final is dominated by a handful of lottery-winner paths (one path ends at 10¹⁵, ten thousand end near zero, and the *mean* is enormous while the *median* is near-bankrupt). Median MDD is the honest summary of "what does the typical path actually feel like."

**Vol-target τ<sub>daily</sub> = 1.0% (5.83×) is the chapter's recommended baseline.** Median MDD 5.9%, p95 MDD 9.2%, mean Sharpe 5.47 (within 2% of the unit-notional Sharpe of 5.53). It captures essentially all the Sharpe of the underlying signal while keeping drawdowns in a range a human or institution can live with. Halving the target to 0.63%/day gets you to 3.67× leverage and 5.9% p95 MDD — a different point on the same curve, equally defensible.

The halt-on-10% row shows the cost of the most conservative stop: a Sharpe of 0.02. The strategy is permanently disarmed by a 10% drawdown that, on the stipulated stationary DGP, is a normal statistical event. Use stops only when you have a real regime-change hypothesis (Ch15).

## §8 — So what?

Three decision rules this chapter unlocks:

1. **Compute Kelly. Then check f̂\*·σ̂.** If f̂\*·σ̂ ≪ 1 (say, < 0.02), divide f̂\* by 2-4 (under-bet because μ̂ is noisy). If f̂\*·σ̂ is not ≪ 1, **do not size with Kelly** — use it only as a leverage ceiling and pick your actual size by vol targeting.
2. **Convert position size to a daily vol target.** It is much easier to defend "this position runs at 1% daily vol" to a risk committee or a co-PM than "this position is at 5× Kelly." Vol targeting drops the μ dependence and exposes a single, intuitive knob.
3. **Run an MC ruin simulation before going live.** Generate 10,000 paths under your sizing rule with synthetic returns matching your edge and σ. Read P(DD ≥ Y%) at your tolerance threshold. If it is above what you (or your investors) can stomach, reduce size — regardless of what the Sharpe says. Use EVT to extrapolate to DD thresholds the MC has not seen.

### What this chapter cannot yet tell you

- **σ̂<sub>t</sub> in §4 is a flat 20-day rolling estimator.** Realized vol is autocorrelated (Ch2 vol clustering) and has intraday seasonality (high at open and close, low midday). A vol-targeting σ̂<sub>t</sub> that exploits this structure responds faster to regime shifts and runs closer to target between shifts. That is Ch15.
- **The stipulated strategy is synthetic.** Ch16 stops working on stipulated cousins and hunts for real positive-EV candidates — momentum, breakout, event-driven — that survive the Ch12-Ch13 cost / execution bar. When one is found, the sizing rules in this chapter apply to it directly.
- **The drawdown-stop finding is conditional on stationarity.** On a non-stationary strategy where the DGP can change, halve-on-X% and halt-on-X% earn their keep as regime-change detectors. The right design of such stops — what X to pick, how to re-enter, how to combine with a separate regime estimator — is a Ch15 / Ch16 question.

## Key Terms

| Term | Definition |
|---|---|
| Bet size | The fraction of equity (or fixed dollar amount) committed to a single trade. Distinct from leverage, which aggregates across positions. |
| Leverage | Ratio of total exposed notional to equity. A leverage multiplier of 5× means $5 of position per $1 of equity. |
| Kelly criterion | Bet-sizing rule that maximizes long-run expected log-wealth growth. Two forms: Bernoulli f\* = (bp − q)/b and continuous f\* = μ/σ². |
| Full Kelly | The Kelly-optimal fraction itself (k = 1). Theoretically growth-maximizing; in practice over-levered due to μ-estimation noise and Taylor-expansion breakdown on bp-scale returns. |
| Fractional Kelly | A scaled-down Kelly bet (k·f\* for k ∈ (0, 1)). Trades expected growth for reduced drawdown variance. Quarter-Kelly is a common practitioner ceiling. |
| Fixed-fractional sizing | Bet a fixed fraction of equity per trade, sized by stop distance: size = (r<sub>per_trade</sub> · equity) / d. Ignores μ; bets equal risk. |
| Volatility targeting | Set leverage so per-period PnL has a stated σ target: size = (τ<sub>daily</sub> · equity) / σ̂<sub>t</sub>. The chapter's recommended baseline. |
| Drawdown stop | A rule that reduces or halts position sizing when running drawdown from peak exceeds a threshold (e.g., halve-on-5%, halt-on-10%). A regime-change detector, not a growth tool. |
| Risk of ruin | Probability of breaching a terminal-loss threshold (e.g., 50% drawdown, account bust) over a stated horizon. Estimated by MC; extrapolated to deep tails by EVT. |
| Expected log-wealth growth rate | g = E[log(W<sub>t+1</sub>/W<sub>t</sub>)]. The objective Kelly maximizes; the right objective for a strategy compounding its own capital. |
| f·σ diagnostic | Per-trade equity-at-risk per σ of return. When f·σ is not ≪ 1, Kelly's Taylor expansion has broken down and the textbook formula is informational only. |
| GPD shape ξ | Tail-domain indicator from a Generalized Pareto fit. ξ < 0 bounded (Weibull), ξ = 0 exponential (Gumbel), ξ > 0 heavy (Fréchet / Pareto). The headline EVT parameter. |
| Drawdown / max drawdown (MDD) | Drawdown at time t is the fractional decline from the running equity peak: (peak − equity<sub>t</sub>) / peak. Max drawdown (MDD) is the largest such value observed over a path. The headline path-functional risk metric. |
| DGP (data-generating process) | The joint distribution producing each trade's return — μ, σ, tail shape, autocorrelation structure. Sizing rules in this chapter assume a stationary DGP; Ch15 / Ch16 relax that. |

## Up next

**Ch15 — Intraday volatility and regime detection.** §4's σ̂<sub>t</sub> is the chapter's biggest unmodeled input. Ch15 refines it with GARCH, intraday seasonality, and explicit regime detection — the same vol-target formula, a much better input. The drawdown-stop reframe (§5) also opens up: stops as regime-change detectors require an actual regime detector, which Ch15 builds.

**Ch16 — Momentum, breakout, and event-driven strategies.** The stipulated cousin used in this chapter has μ = 1 bp because the real Ch7-Ch13 strategy has μ ≈ 0 after costs. Ch16 hunts for strategy families whose pre-cost edge is large enough to survive the Ch12-Ch13 cost stack — and applies the sizing rules from this chapter to whatever it finds.

## Exercises

1. **Kelly's sensitivity to μ misestimate.** SE on μ̂ from
   N=1,500 trades is σ/√1500 ≈ 1.81×10⁻⁵.
   Compute f\*(μ̂) = μ̂/σ² and growth rate
   g(f\*) = f\*·μ<sub>true</sub> − ½·(f\*)²·σ²
   at each f\* (using the *true* μ). Plot f\*(μ̂) and
   g(f\*(μ̂)) over μ̂ ∈ [μ − 2·SE, μ + 2·SE].
   Show that +1-SE optimism over-states leverage by ~18% and
   costs ~3% of peak growth; +2-SE optimism over-states leverage
   by ~36% and costs ~13% of peak growth. Identify the
   μ̂ at which g(f\*) = 0 and express it in SE units (it
   sits well outside the ±2·SE band).
2. **Vol targeting under regime shift.** Generate a synthetic 1-year
   session-bar series where true σ doubles at t=0.5. Run
   vol targeting with 20-day rolling σ̂<sub>t</sub> and
   τ<sub>daily</sub>=1%. Plot realized-vol vs target-vol; document the
   lag (in days) before realized catches up, and the over-leveraged
   window's max DD.
3. **Empirical-MC vs GPD-extrapolated P(DD ≥ 20%).**
   Compute both on the stipulated strategy *at vol-target leverage
   5.83×* (not full-Kelly — full-Kelly saturates MC). Then redo with
   Student-t(df=4) per-trade returns at matched variance. Document
   the gap that opens at deep-DD thresholds (P(DD ≥ 30%),
   P(DD ≥ 50%)) when the tail is fat.
4. **Half-Kelly vs vol-target at matched ex-ante leverage.** Pick
   τ<sub>vol</sub> such that vol-target's leverage equals half-Kelly's
   leverage (~102 here). Compare max-DD distributions. Which is
   preferable and why? (Hint: they should be near-identical because
   at matched leverage they bet the same fraction; the framing
   differences vanish — at the same leverage, both rules produce
   statistically identical paths.)
