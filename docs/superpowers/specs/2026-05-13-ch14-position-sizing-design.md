# Chapter 14 Design — Position Sizing & Risk of Ruin

**Date:** 2026-05-13
**Status:** Approved (Part 8 opener — sizing, regime, more strategies).
**Spine:** First chapter of Part 8. Ch8-13 produced a forensic deflation arc on one mean-reversion strategy and closed at after-execution Sharpe −1.11 — Kelly = 0, don't trade. Ch14 generalizes the *sizing question*: given any positive-expectancy strategy, how much capital to commit per trade, per unit time, and how to protect against ruin. The strategy distribution is **stipulated synthetic** so the math has something to teach against; the framework is what carries forward.

## Why this chapter exists

The Ch8-13 arc answered "is this edge real?" with "no, after costs and execution." It taught a discipline: the cost stack and execution model deflate Sharpe more than parameter optimization ever inflates it. But every shipped chapter assumed **unit notional** — one share, one contract, one fixed bet — when computing Sharpe. Real trading must decide *size*, and size has its own deflation arc:

- Bet too small: positive edge produces negligible dollars.
- Bet too large: realized PnL volatility dominates expected return; max drawdown exceeds psychological or institutional tolerance; in the limit, ruin.

The chapter answers three operational questions:

1. **How much per trade?** — Kelly, fractional Kelly, fixed-fractional.
2. **How much risk per unit time?** — volatility targeting.
3. **When do I stop?** — drawdown-stop rules, risk-of-ruin via Monte Carlo and EVT.

The EVT salvage from retired Ch10 lands as a tight §6 sidebar: fit GPD to the synthetic trade-PnL left tail, extrapolate ruin probability, compare to raw MC ruin frequency.

## The stipulated strategy

Ch13 closed at Sharpe −1.11, so Kelly on Ch13's strategy is degenerate (μ ≤ 0 → f\* ≤ 0 → don't trade). The chapter opens with this fact stated honestly, then **stipulates a positive-EV cousin** so the sizing math has something to size against:

- Per-trade mean: μ = **+1.0 bp** (10× Ch11's pre-cost +0.16 bp, picked so a 1 bp cost wedge doesn't sign-flip the strategy)
- Per-trade std: σ = **7.0 bp** (matches Ch11/Ch12 measurements)
- Trades per session: ~6 (matches Ch8 trade-rate)
- Sessions per year: 252
- ⇒ Per-trade Sharpe ≈ 0.143; annualized Sharpe ≈ **0.143 × √(6 × 252) ≈ 5.6** unit-notional

The 5.6 number is unrealistically high *by design* — the chapter wants the sizing rules to bite via leverage choice, not be obscured by signal noise. Ch16's hunt for a real candidate gets a separate, deflated bar.

Returns are simulated as i.i.d. Normal (with optional Student-t alternative for §6 EVT). The i.i.d. assumption is documented as a limit (Ch7's lag-1 ρ tells us trades are not perfectly independent; Ch15's regime detection is where the chapter would relax this).

## Three-flavor framing

1. **How much per trade?** (Kelly, fractional Kelly, fixed-fractional)
2. **How much risk per unit time?** (volatility targeting)
3. **When do I stop?** (drawdown-stop rules, risk-of-ruin)

Each flavor maps to a different *primitive* the trader controls: trade-level leverage, period-level leverage, and an exit policy on the equity curve.

## Section structure

### §1 — Setup: the stipulated strategy

State the disclaimer (Ch13 → Kelly=0; Ch14 stipulates a positive-EV cousin so the math teaches). Lay out μ, σ, trades/session, sessions/year. Show the unit-notional equity curve once for orientation. Forward-pointer: Ch16 will hunt for a real candidate; until then, the strategy is a teaching fixture.

### §2 — Per-trade sizing: Kelly

The bet-level question. Derivation sketch:

- **Bernoulli form.** f\* = (bp − q)/b where p = win prob, q = 1 − p, b = win:loss payoff ratio. Plain English: "edge over odds." Reused from Ch7 §1 expectancy framing.
- **Continuous form.** For a normally distributed per-trade return r ~ N(μ, σ²), the log-wealth-maximizing fraction is f\* = μ/σ². Derivation in `<details>`: maximize E[log(1 + f·r)] via second-order Taylor, set derivative to zero.

Where-clause symbol legend on every formula (per `feedback_define_formula_symbols`).

**Worked numbers on the stipulated strategy.** μ/σ² = 1.0 bp / (7.0 bp)² = 1e-4 / 4.9e-3 = **0.0204 per trade**, i.e. ~2% of equity per trade as the growth-optimal full-Kelly bet. Over a 252-day year at 6 trades/day, that compounds aggressively but with the maximum drawdown distribution Kelly is famous for.

**Why nobody runs full-Kelly.**
1. **μ is estimated.** A +1 SE shift on μ̂ collapses the implied f\* by 50% or more — Exercise 1 demos this directly.
2. **Fat tails.** Kelly's Taylor expansion assumes well-behaved σ²; under fat tails the second-order approximation under-states downside.
3. **Max-DD pain.** The classical Kelly result: P(max DD ≥ x) = 1 − x for x ∈ [0, 1] over an infinite horizon. So full-Kelly has a 50% chance of hitting −50% DD eventually. Most humans/institutions tap out long before then.

**Growth-rate-vs-leverage plot.** g(kf\*) = kf\*·μ − ½(kf\*)²·σ² as a function of multiplier k. Peaks at k=1 (full-Kelly); zero at k=2; negative beyond. The "overbetting collapse" picture.

**Half-Kelly / quarter-Kelly.** Standard practitioner defaults. At half-Kelly: growth is 75% of optimal but max-DD distribution roughly halves. Document the trade-off.

### §3 — Per-trade sizing alternatives

**Fixed-fractional.** Risk a fixed fraction *r* of equity per trade given a stop distance *d*:
size = (r · equity) / d. The retail-textbook default ("never risk more than 2% per trade"). Where it differs from Kelly: ignores μ entirely, sizes purely off downside.

**Fixed-dollar.** Constant notional. Useful as a baseline; doesn't compound; doesn't adapt to drawdowns.

**Comparison.** When stop distance *d* is roughly constant across trades (as in the stipulated strategy with σ-based stops), fixed-fractional and Kelly are linearly related. When stop distance varies (variable signal strength), they diverge — fixed-fractional bets equal *risk*, Kelly bets equal *edge/risk²*.

### §4 — Per-period sizing: volatility targeting

The portfolio-level workhorse. Pick an annualized target vol *τ* (e.g., 10%); size each position so its forecast contribution to portfolio vol equals τ:

size_t = (τ_daily · equity) / σ̂_t

where σ̂_t is the realized-vol forecast for the next period. On the stipulated strategy with daily PnL std ~ 7 bp · √6 ≈ 17 bp, a 1% daily-vol target implies leverage ≈ 1.0%/0.17% ≈ 5.9×.

**Choice of σ̂_t.** This chapter uses rolling 20-day realized std as a placeholder. Forward-pointer: Ch15 refines σ̂_t with GARCH and intraday seasonality — the same input plugs into the same formula.

**Regime sensitivity.** A doubling of true σ with the σ̂_t estimator unchanged means actual leverage is double-target. Exercise 2 demos this on a synthetic regime change.

**Relation to Kelly.** Vol targeting is essentially "Kelly with a stipulated leverage budget instead of a derived one." The two reconcile when target_vol = √(μ²/σ²) — but vol targeting drops the μ dependence, which is the noisiest input.

### §5 — Drawdown control

Equity-curve simulation under each sizing rule (1,000 Monte Carlo paths over 1 year):

- Fan chart per rule (p5 / p50 / p95 equity over time)
- Max-DD distribution per rule
- Average / median / p95 max DD comparison table

**Drawdown-stop rules.** Concrete worked rules:
- **Halve-on-5%-DD.** If trailing equity DD ≥ 5%, halve all sizes until equity recovers to within 2% of peak.
- **Halt-on-10%-DD.** If trailing equity DD ≥ 10%, stop trading entirely.

Simulate the same MC paths with stops applied. Headline expected finding: stops sacrifice 10-20% of mean growth but cut p95 max DD by roughly half.

**Honest caveat.** Drawdown stops are a *behavioral* control: they reduce ruin probability and psychological pain at the cost of expected growth. Whether to use them is a utility-function question, not a math question.

### §6 — Risk-of-ruin sidebar (EVT salvage)

The retired Ch10 salvage. Tight scope: one section, ~1 page.

**Problem.** What's P(max DD ≥ 20%) over a year on the stipulated strategy? Two answers:

1. **Empirical Monte Carlo.** Run 10,000 paths, count the fraction with max DD ≥ 20%. Concrete number, but with sampling error — and at very deep DDs (30%, 40%) the empirical count gets noisy fast.
2. **EVT extrapolation.** Fit a generalized Pareto distribution (GPD) to the lower tail of per-trade PnL. Use GPD-implied tail probabilities together with a random-walk drawdown approximation (cumulative-sum maximum on a sequence with stipulated mean and a GPD-fitted tail) to estimate P(max DD ≥ X) at depths beyond the empirical reach.

Show the GPD fit on the synthetic tail, the EVT-extrapolated P(DD ≥ X) for X ∈ {10%, 20%, 30%, 50%}, and the MC empirical counts as a sanity check. Headline expected finding: at 20% the two agree closely; at 50% MC has near-zero count but EVT gives a small-but-positive estimate. EVT is the right tool when you want to extrapolate beyond what's been observed.

This sidebar pays the **EVT salvage** debt from the 2026-05-07 pivot.

### §7 — Side-by-side comparison

The synthesis section. Same stipulated strategy, all sizing rules, single table:

| Rule | Mean final equity | Median max DD | p95 max DD | P(DD ≥ 20%) | Equity Sharpe |
|------|-------------------|---------------|------------|--------------|----------------|
| Unit notional | ... | ... | ... | ... | ... |
| Full Kelly | ... | ... | ... | ... | ... |
| Half Kelly | ... | ... | ... | ... | ... |
| Quarter Kelly | ... | ... | ... | ... | ... |
| Fixed-fractional 2% | ... | ... | ... | ... | ... |
| Vol-target 10% | ... | ... | ... | ... | ... |
| Half-Kelly + halve-on-5% | ... | ... | ... | ... | ... |

Headline expected finding: half-Kelly with a halve-on-5% stop sits in the sweet spot — Sharpe roughly unchanged from full-Kelly, max DD distribution dramatically tighter.

### §8 — So what + Key Terms + Up next

**So what?** Three decision rules the chapter unlocks:
1. Given a strategy with measured μ̂ and σ̂, compute Kelly. Then divide by 2-4 because μ̂ is noisy.
2. Convert position size to a vol-target — much easier to defend "this position runs at 10% annualized vol" than "this position is 5× Kelly."
3. Run an MC ruin simulation before going live. If P(DD ≥ Y%) > tolerance, reduce size.

**What this chapter can't yet tell you:** the σ̂_t forecast in §4 uses a flat 20-day rolling estimator. Realized vol is autocorrelated (Ch2 vol clustering), so a better σ̂_t adapts to the recent regime — that's Ch15. And the strategy itself is stipulated synthetic; Ch16 looks for real positive-EV candidates beyond the mean-reversion family.

**Key Terms (target 10).** Bet size, leverage, Kelly criterion, full Kelly, fractional Kelly, fixed-fractional sizing, volatility targeting, drawdown stop, risk of ruin, expected log-wealth growth rate.

**Up next.** Ch15 refines §4's σ̂_t with intraday vol seasonality + GARCH. Ch16 hunts for a real positive-EV strategy that survives the Ch12-13 cost/execution bar.

## Data

No new pulls. Strategy ledger generated via `numpy.random.default_rng(seed=14)` against the stipulated (μ, σ). Optional anchor read of Ch11 walk-forward ledger for sanity-comparison of synthetic vs real magnitudes (read-only).

EVT sidebar fits GPD on the synthetic tail; optionally also fits on Ch11's real trade ledger as a secondary comparison.

## Dependencies

- `numpy`, `scipy` (already installed; scipy.stats.genpareto for §6)
- `pandas` (already installed; ledger handling)
- `matplotlib` (already installed; fan charts, growth-rate plot)

No new dependencies.

## Exercises

Following `feedback_exercises_bottom_and_matched`: prompts in README/lesson/merged match 1:1; worked solutions in merged follow prompts where lesson has them.

1. **Kelly's sensitivity to μ misestimate.** Given σ̂ exactly known, vary μ̂ by ±1 SE (computed from N=1,500 trades). Plot f\*(μ̂) and growth-rate g(f\*(μ̂)) using true μ. Show that the +1-SE optimistic estimate produces ~2× the prescribed leverage and *negative* growth at full-Kelly.
2. **Vol targeting under regime shift.** Construct a synthetic series where true σ doubles at t = 0.5. Run vol targeting with 20-day rolling σ̂_t and target_vol = 10%. Plot realized vs target vol; document the lag and the over-leveraged window.
3. **Empirical-MC vs GPD-extrapolated P(DD ≥ 20%).** Compute both on the stipulated strategy. Then redo with a Student-t per-trade distribution (df=4) and document the gap that opens.
4. **Half-Kelly vs vol-target at matched ex-ante leverage.** Pick target_vol so vol-target's average leverage equals half-Kelly's leverage. Compare max-DD distributions and equity Sharpes. Which is preferable and why?

Worked solutions for Exercises 1 and 3 in the lesson notebook (the others stay as prompts only).

## Promises honored

- **Ch11 §7** "Ch14 (sizing) uses the walk-forward expectancy as Kelly's input" — partially: chapter acknowledges Ch13's verdict (Kelly = 0 on the real strategy) and instead sizes against a stipulated positive-EV cousin. The Ch11 ledger informs the synthetic distribution parameters.
- **Ch12 §promises** "Kelly with negative-budget input is degenerate; chapter assumes a positive-expectancy strategy" — honored explicitly in §1.
- **Ch13 §promises** "Kelly takes after-execution expectancy as input. Here it's negative → Kelly = 0; the framework still matters for the next strategy that survives" — honored explicitly in §1.
- **Pivot 2026-05-07** "EVT salvage sidebar" — paid in §6.
- **Ch5 drawdown** taxonomy — §5 reuses the running-peak / underwater-curve machinery from Ch5 on the equity-curve MC paths.
- **Ch7 §1 expectancy** — §2 Bernoulli Kelly is the same edge/odds quantity Ch7 §1 introduced; chapter cross-references explicitly.

## Promises to honor in later chapters

- **Ch15** refines §4's σ̂_t with GARCH + intraday seasonality; same vol-target formula, better σ̂_t input.
- **Ch16** hunts for real positive-EV strategies; each one gets sized using the framework Ch14 built. Ch14's stipulated 5.6 Sharpe is unrealistic; Ch16's candidates will be much closer to zero.
- **Ch17-18** Kelly with futures-contract granularity: position size rounds to integer contracts, which can dominate the sizing math at small accounts. Risk-of-ruin under contract-rounding is the going-live version of §6.

## Pedagogical notes

- **Concept before statistics** (`feedback_concept_before_statistics`): name the three operational questions in §1 before any formula appears; recap by question in §8, not by formula.
- **Define every term on first use** (`feedback_define_every_term`): "log-wealth," "growth rate," "GPD," "leverage" all get inline glosses + Key Terms entries.
- **Define every formula's symbols** (`feedback_define_formula_symbols`): each Kelly form, the vol-target formula, the GPD density, all carry a where-clause.
- **Push interpretations past description** (`feedback_push_interpretations_past_description`): every plot gets a "what this means for the next position you take" paragraph, not just "the curve peaks at k=1."
- **No external knowledge leaps** (`feedback_no_external_knowledge_leaps`): "log-wealth growth rate" needs explicit framing — Kelly's optimality criterion is *not* expected wealth, and that distinction matters. "GPD" and "Pareto tail" similarly get rebuilt inline rather than assumed from retired Ch10.
- **Comment non-obvious code** (`feedback_comment_nonobvious_code`): MC simulation loops, GPD fit calls, equity-curve drawdown helpers all get brief `#` comments.

## Expected mid-execution course corrections

Continuing the chapter-arc pattern (Ch4-Ch13 every chapter had at least one). Likely candidates:

1. **Half-Kelly vs quarter-Kelly trade-off.** The "half-Kelly is the sweet spot" claim is folk wisdom; on the stipulated distribution it might come out closer to quarter-Kelly once max-DD distributions are compared honestly. Be ready to update §2's recommendation.
2. **GPD-vs-MC agreement on the synthetic tail.** With an i.i.d. Normal generator, the GPD ξ̂ should be ~0 (Gumbel domain) and EVT and MC should agree closely at all DD levels. The interesting separation only opens up under fat-tailed input — that's Exercise 3's job. If §6's headline becomes "EVT and MC agree because the input is Normal," reframe §6 around "EVT *as insurance* — it costs nothing to fit when the tail is thin, but it's the right tool when the tail is fat."
3. **Vol-target leverage at the stipulated 5.6 Sharpe.** Implied leverage could be very high (50×+) because the Sharpe is unrealistically clean. Document explicitly and adjust the target_vol downward for the worked examples if it produces nonsensical equity paths. The framework is the lesson, not the specific number.
4. **Drawdown-stop benefit might disappoint.** On an i.i.d. positive-EV series, stops *reduce* expected growth without much DD benefit (a stop fires on a random unlucky run, not a regime change). If MC says stops cost more than they save, reframe §5 around "stops are insurance against the i.i.d. assumption being wrong" and explicitly connect to Ch15's regime detection.

The shape-of-correction pattern (plan target X, reality Y, reframe narrative) is itself part of the curriculum's authorial voice and gets documented inline.
