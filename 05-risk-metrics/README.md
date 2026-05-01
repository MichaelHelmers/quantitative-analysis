# Chapter 5 — Risk Metrics: Drawdown, VaR, Sharpe

> **Goal of this chapter:** the *summary numbers*. Four chapters built the raw materials — returns (Ch1), volatility and fat tails (Ch2), correlation (Ch3), an honest expected-return estimator with error bars (Ch4). This chapter compresses those raw materials into three decision-relevant scalars.

The chapter has three main parts. **§2 (drawdown)** pays Ch1's "we'll formalize later" debt — running peak, drawdown series, max drawdown, recovery time. **§3 (VaR and CVaR)** restates Ch2's fat-tail finding as a *quantile-dependent* tail premium: at conventional confidence levels the Gaussian approximation is fine; the divergence appears, and grows, deeper into the tail. **§4 (Sharpe)** pays Ch3's promise *and* integrates Ch4's noise-of-the-mean machinery — the chapter's punchline is that two strategies with point Sharpes differing by ~0.2 are statistically indistinguishable at 20-year sample sizes.

The chapter uses the same 8-ticker basket as Chapters 3–4 — **SPY, TLT, GLD** plus five US sector ETFs (**XLK, XLF, XLE, XLV, XLU**) — over 20 years. We add one new series: `^IRX`, the annualized 13-week T-bill yield, used as the risk-free rate.

---

## What we mean by "a risk metric"

There isn't one universal risk number. There are several, each summarizing a different *flavor* of risk. Chapter 2 named four flavors of risk itself (magnitude, persistence, path/drawdown, correlation); this chapter introduces the metrics that compress them into scalars:

| Risk-metric flavor | What it summarizes | Ch2 risk-flavor it formalizes |
|---|---|---|
| **Path risk** — drawdown, recovery time | The worst the price path got, and how long until it healed. | Path / drawdown (Ch2 deferred this; Ch5 pays it off). |
| **Tail risk** — VaR, CVaR | How bad a worst-q% day looks; how bad the *average* breach is. | Magnitude (one-day moves) + fat tails (a *quantile-dependent* gap between historical and parametric VaR). |
| **Risk-adjusted return** — Sharpe | Return per unit of risk; the simplest "is the reward worth it?" number. | Magnitude (vol) combined with Ch4's expected return. |

**Correlation-flavor risk metrics** (factor exposure, beta) are the natural fit for Ch8's CAPM / Fama–French treatment. They're flagged here only so the reader knows the taxonomy isn't complete with three.

---

## 1. Setup

Same library stack and same 8-ticker basket as Chapter 4 — no new dependencies. We hold both **prices** (for drawdown — which is a price-level concept, not a return-level one) and **log returns** (for vol and Sharpe).

The one new data series is **`^IRX`**, the annualized 13-week T-bill yield, served as a percentage by yfinance. Two conversions get it to a daily decimal: divide by 100 (percent → fraction), then by 252 (annualized → per-day).

### What is a T-bill, and why is its yield "risk-free"?

A **T-bill** (Treasury bill) is short-term US government debt — typically 4-, 13-, or 26-week maturities. Default risk is negligible at these horizons (the US Treasury hasn't defaulted on dollar obligations), so the T-bill yield is the standard real-world proxy for "risk-free in dollar terms" — what you can earn doing nothing risky. The 13-week yield is the most common Sharpe-ratio convention.

Over the 20-year window, *r<sub>f</sub>* ranged from **near 0%** (zero-interest-rate periods after the GFC and during COVID — the **ZIRP** era from late 2008 to ~2015, plus 2020–2021) to **roughly 5%** (just before the GFC; again from late 2022 onward as the Fed hiked to fight inflation). Using a constant *r<sub>f</sub>* for any portion of this window distorts results badly, so we use the rolling daily series.

After the setup cells run, expect:
- 8-column return panel with **~5,000 daily observations** spanning ~20 years (continuity with Ch3 and Ch4).
- An aligned `rf_daily` series with the same index.

§2 uses the SPY price path. §3 uses SPY daily returns. §4 uses Ch3's 60/40 (SPY/TLT) and equal-weight-8 portfolios plus `rf_daily` to compute excess returns and Sharpes.

## 2. Drawdown — the path-risk metric

The price path doesn't go up monotonically. From any local peak, it falls some amount before reaching a new peak. The **drawdown** at time *t* is how far below the running peak the price currently sits. **Max drawdown (MDD)** is the worst such value over a window.

Why path matters separately from magnitude: an asset with 15% annualized vol can spend 18 months down 50%. Vol describes one-day pain; drawdown describes worst-case cumulative pain. They're different numbers measuring different things.

### 2.1 Formal definitions

> *P*<sub>peak</sub>(*t*) = max<sub>*s* ≤ *t*</sub> *P*(*s*)
>
> *DD*(*t*) = (*P*(*t*) − *P*<sub>peak</sub>(*t*)) / *P*<sub>peak</sub>(*t*)
>
> *MDD* = min<sub>*t*</sub> *DD*(*t*)

where:
- *P*(*t*) — price (or portfolio value) at time *t*. **Units:** dollars.
- *P*<sub>peak</sub>(*t*) — running peak: the highest *P*(*s*) seen up to and including *t*. Same units.
- *DD*(*t*) — the drawdown at time *t*. **Units:** decimal fraction, always ≤ 0.
- *MDD* — the most negative *DD*(*t*) over the window. Same units as *DD*.

> **Foot-gun: sign convention varies in practice.** Some packages report MDD as a positive percentage (55%), some as a positive fraction (0.55), some as a negative decimal (−0.55). All three are common; pick one — we use **negative decimals** — and label every plot.

### 2.2 SPY drawdown over 20 years

Computing the running peak, drawdown series, and MDD for SPY produces an MDD of **−55.2%**, with the trough on **2009-03-09** and the preceding peak on **2007-10-09**. The notebook plots the price + running peak together, and a separate **underwater curve** showing the drawdown over time.

The biggest underwater stretch is the **Global Financial Crisis (GFC)** drawdown — peak in October 2007, trough in March 2009 (−55.2%). The GFC was a financial-sector crisis triggered by the collapse of the US subprime mortgage market and the failure of Lehman Brothers in September 2008.

The secondary trough is the **COVID crash** in March 2020 (−33.7%). Pandemic-induced economic shutdowns drove an unusually fast and unusually deep selloff that recovered within months — a totally different *shape* of drawdown than the GFC's slow grind. The third-deepest is the **2022 rates-regime drawdown** (−24.5%) — the Fed hiked aggressively to fight post-COVID inflation, which directly hurt long-duration assets and dragged broad equities along.

### 2.3 Recovery time

Drawdown depth alone misses half the story. **Time-to-recovery** — days between the peak preceding a drawdown and the first new peak after — captures duration. The notebook tabulates SPY's top-3 drawdowns by depth with their recovery times:

| Rank | Peak date | Trough date | Drawdown | Days peak → trough | Days peak → recovery |
|---|---|---|---|---|---|
| 1 | 2007-10-09 | 2009-03-09 | −55.2% | 517 | 1,773 (~4.9y) |
| 2 | 2020-02-19 | 2020-03-23 | −33.7% | 33 | 173 (~6 mo) |
| 3 | 2022-01-03 | 2022-10-12 | −24.5% | 282 | 709 (~2y) |

The GFC was both deep *and* slow to heal. COVID was nearly as deep at the moment but the path resolved within months. The 2022 drawdown was shallower but still took two years from peak to new high. Path risk has two coordinates, not one — a reader who only saw the depth column would treat GFC and COVID as similar; the duration column tells a very different story.

### 2.4 What this means with $100k

A **$100,000** position in SPY held from October 2007 through March 2009 would have shown roughly **$45,000** on the screen at the trough. The investor doesn't get to wave the next four-plus years of recovery away — they had to *sit through* the drawdown, with no guarantee of recovery, while watching their stated value more than halve.

Vol alone wouldn't have predicted that. SPY's annualized vol over the window was ~20% — but vol is a one-day number; drawdown is the multi-year cumulative-path number. They measure different things, and a position-sizing decision driven only by vol is missing half the picture.

## 3. Tail risk — VaR and CVaR

"How bad is a bad day?" admits two useful answers, and you want both:

- **Value at Risk (VaR)** — the threshold: "5% of days are at least this bad." A *quantile* of the loss distribution.
- **Conditional VaR (CVaR), aka Expected Shortfall (ES)** — the average past the threshold: "*given* that today is in the worst 5%, how bad is it on average?" The *expected value* conditional on being in the tail.

VaR is the most-cited tail-risk metric in industry. It's also famously blind to the shape of the tail past the threshold — two assets with the same 5% VaR can have wildly different 1% tails. CVaR addresses that shape blindness.

### 3.1 Historical VaR

Historical (empirical) VaR makes no distributional assumption — just count quantiles in the data:

> *VaR*<sub>α</sub> = − *Q*<sub>α</sub>(*r*)

where:
- *α* — the **confidence level** (more precisely, the tail probability), a fraction in (0, 1). Typical values: 0.05 (one-in-twenty days) or 0.01 (one-in-a-hundred days).
- *Q*<sub>α</sub>(*r*) — the α-quantile of the historical return distribution. **Units:** decimal return.
- The leading minus turns a *negative-quantile return* into a *positive loss*, by convention.

> **Foot-gun: VaR sign and reporting convention.** "5% VaR of 1.8%" means **losses of at least 1.8% on 5% of days**. Some practitioners flip the sign or report VaR as the negative quantile directly. Pick one — we use **positive losses** — and label every plot and table.

For SPY over 20 years, the historical 5% VaR is roughly **1.8%** and the 1% VaR is roughly **3.6%** (per day, log-return scale).

### 3.2 Parametric (Gaussian) VaR — and where it matches, and where it breaks

If returns were normal, the α-quantile sits a fixed number of standard deviations below the mean:

> *VaR*<sub>α</sub><sup>Gaussian</sup> = − (*μ* + *z*<sub>α</sub> · *σ*)

where:
- *μ* — sample mean of returns. **Units:** decimal return per period.
- *σ* — sample standard deviation of returns. Same units.
- *z*<sub>α</sub> — α-quantile of the **standard normal** distribution (the normal with mean 0 and standard deviation 1). For 5%: *z*<sub>0.05</sub> ≈ −1.645. For 1%: *z*<sub>0.01</sub> ≈ −2.326.
- *VaR*<sub>α</sub><sup>Gaussian</sup> — VaR under the normal-returns assumption. Same units.

> **Foot-gun: assumes normality.** Chapter 2 demonstrated that daily equity returns are *not* normal — they have fat tails. The natural expectation is that Gaussian VaR underestimates tail risk uniformly. **The data tells a more nuanced story:**

| Quantile | Historical VaR | Gaussian VaR | Ratio (hist / Gaussian) |
|---|---|---|---|
| 5% | 1.82% | 1.97% | **0.92** |
| 1% | 3.64% | 2.81% | **1.30** |
| 0.5% (Exercise 2) | 4.60% | 3.11% | **1.48** |

**At the 5% level, Gaussian VaR is essentially indistinguishable from historical VaR — slightly *higher* if anything.** The "fat tails make Gaussian wrong" intuition only kicks in deeper into the tail. At 1% the Gaussian model underestimates by ~30%; at 0.5% by ~50%; further out the gap keeps growing.

This is a more honest restatement of Ch2's finding than "Gaussian always underestimates tail risk." Fat tails aren't a uniform multiplier on risk — they're a divergence in *shape* that appears in the deep tail. **The gap between historical and Gaussian VaR is the quantitative tail premium, and it is itself a function of how deep into the tail you go.** Conventional 95%-confidence VaR happens to be *just* close enough to where the tails of a normal end that the approximation holds; 99% is already where it visibly fails; deeper is where it fails badly.

The practical takeaway: **for shallow VaR (5%), parametric is fine. For deep VaR (1% and beyond), use historical.** And for any quantile, *also* report CVaR — because what's behind the threshold matters even when the threshold itself looks tame.

### 3.3 CVaR / Expected Shortfall

VaR is a threshold; CVaR is the average past it:

> *CVaR*<sub>α</sub> = − E[*r* | *r* ≤ *Q*<sub>α</sub>(*r*)]

where:
- *r* — daily return.
- *Q*<sub>α</sub>(*r*) — the α-quantile (the same threshold used in VaR).
- *CVaR*<sub>α</sub> — expected loss given that the day is in the worst α%. **Units:** decimal loss.

> **Foot-gun: CVaR ≥ VaR by construction.** The conditional mean of values past a threshold is always at least as far from the center as the threshold itself.

For SPY: 5% CVaR ≈ **3.0%**; 1% CVaR ≈ **5.4%**. A useful frame: **the average bad day in the worst-5% bucket is roughly as bad as the 1% VaR threshold itself.** This is exactly where the fat-tail divergence shows up — even if 5% VaR looks Gaussian-like, the 5% *CVaR* (which averages over the deeper tail past the 5% threshold) lands well into the territory where Gaussian fails.

### 3.4 What this means with $100k

A $100k SPY position has, very roughly:
- **5% VaR ≈ $1,800** — once or twice a month on average, you'll lose at least that much.
- **1% VaR ≈ $3,600** — two or three times a year, you'll lose at least that much.
- **5% CVaR ≈ $3,000** — on the *average* day in the worst-5% bucket, the loss is around $3,000.
- **1% CVaR ≈ $5,400** — and on the average day in the worst-1% bucket, you lose roughly the *2× the 1% VaR threshold*.

The honest framing is the CVaR one: VaR alone tells you the threshold; CVaR tells you what's behind it. A risk policy that uses only VaR ("we never want to lose more than $X with 95% confidence") will be repeatedly surprised by what happens when the threshold is crossed — because the *average* breach is much worse than the threshold itself.

## 4. Sharpe — the risk-adjusted-return metric

Two assets, same vol, different mean returns: the higher mean wins. Two assets, same mean, different vols: the lower vol wins. **Sharpe** is the simplest scalar combining both — return per unit of risk.

### 4.1 Excess returns

Sharpe is computed on **excess returns** — the asset's return *minus* the risk-free rate:

> *r*<sub>excess,t</sub> = *r*<sub>t</sub> − *r*<sub>f,t</sub>

where:
- *r*<sub>t</sub> — the asset's return on day *t*. **Units:** decimal per day.
- *r*<sub>f,t</sub> — the risk-free rate on day *t* (per day, decimal). We use `rf_daily` from §1.
- *r*<sub>excess,t</sub> — the asset's compensation for taking risk on day *t*.

The reason we subtract *r<sub>f</sub>* is that earning, say, 4% in a 4% T-bill environment is *zero compensation for risk* — you could have had it without taking any risk. Sharpe asks how much of the asset's return is *paying you for the volatility you absorbed*, not how much is just there because money costs money.

> **Foot-gun: convert annualized r_f quotes to per-period before subtracting.** `^IRX` is annualized in percent; the §1 setup divides by 100 (percent → fraction) and 252 (annualized → per-day) before the subtraction.

### 4.2 The Sharpe ratio

> *Sharpe* = *μ*<sub>excess</sub> / *σ*<sub>excess</sub>

where:
- *μ*<sub>excess</sub> — the sample mean of excess returns. **Units:** decimal per period.
- *σ*<sub>excess</sub> — the standard deviation of excess returns. Same units. (In practice ≈ *σ*<sub>r</sub>, since *σ*<sub>r_f</sub> is much smaller than *σ*<sub>r</sub>.)

> **Foot-gun: annualizing Sharpe.** Sharpe annualizes by **× √252**, *not* × 252. The numerator scales by 252 (means add); the denominator scales by √252 (vols scale by √t); the ratio scales by 252 / √252 = √252. Mixing these up is one of the more common bugs in quant code — *always* sanity-check the annualized Sharpe against an order-of-magnitude expectation (broad equity Sharpes are typically 0.3–0.7, not 5+).

Annualized Sharpes over the 20y window:

| Asset / portfolio | Annualized Sharpe |
|---|---|
| 60/40 SPY-TLT | 0.524 |
| EW8 (8-ticker equal weight) | 0.477 |
| SPY | 0.452 |
| GLD | 0.425 |
| TLT | 0.113 |

The **60/40** edges out **equal-weight-8** — continuity with Ch3's finding that EW8 over-allocates to high-vol sectors, raising *σ* faster than it raises *μ*. SPY alone is just behind both. GLD's Sharpe is comparable. TLT's is far lower — long-duration Treasuries took heavy damage in the 2022 rates regime, which dragged the 20y Sharpe down to barely above zero.

But before reading too much into the ranking, the next subsection puts honest error bars on the numbers — and **the bands largely overlap.**

### 4.3 Honest CI on Sharpe — and why the bands overlap

Sharpe is a ratio of two estimated quantities. Both are noisy. At our sample sizes the numerator's noise dominates (Ch4 §2 measured this — the SE of the mean shrinks like √N, and the SE of σ shrinks faster). A useful approximation, treating *σ* as known:

> *SE(Sharpe)* ≈ *SE(μ̂*<sub>excess</sub>*)* / *σ*

where:
- *SE(μ̂*<sub>excess</sub>*)* — standard error of the mean excess return, *σ* / √N from Ch4 §2.2.
- *σ* — standard deviation of excess returns.
- *SE(Sharpe)* — approximate standard error of the per-period Sharpe.

Annualizing: *SE(μ̂)* annualizes by × 252 and *σ* by × √252, so *SE(Sharpe)* annualizes by × 252 / √252 = × √252 — the **same scaling as the point estimate**. Build a 95% CI as *Sharpe* ± 1.96 · *SE(Sharpe)* on the annualized scale.

For SPY over 20 years: annualized Sharpe = 0.452, with 95% CI **[0.013, 0.891]**. **The lower bound barely clears zero.** Twenty years of daily data, and the honest 95% CI on SPY's risk-adjusted return spans nearly an order of magnitude.

The notebook plots all five assets / portfolios with their 95% CI error bars:

| Asset / portfolio | Sharpe | 95% CI |
|---|---|---|
| 60/40 SPY-TLT | 0.524 | [0.086, 0.963] |
| EW8 | 0.477 | [0.038, 0.916] |
| SPY | 0.452 | [0.013, 0.891] |
| GLD | 0.425 | [−0.013, 0.864] |
| TLT | 0.113 | [−0.326, 0.552] |

All four equity-flavored CIs overlap heavily. **You cannot reject "60/40 and EW8 have equal true Sharpes" at the 5% level.** GLD's CI even crosses zero — over 20 years, the question "does GLD earn a positive risk-adjusted return after the risk-free rate?" cannot be answered with conventional confidence.

> **Punchline.** At 20-year sample sizes, two strategies whose point Sharpes differ by ~0.05 (60/40 vs EW8 vs SPY) are *statistically indistinguishable*. Even a ~0.4 Sharpe difference (60/40 vs TLT) is borderline. This is exactly Ch4's noise lesson restated for ratios — Sharpe inherits the SE of the mean it's built from. **Compare Sharpes only with their CIs, never naively.**

<details>
<summary>Delta-method derivation of <em>SE(Sharpe)</em> including the σ-noise term</summary>

The simple approximation above treats *σ* as known. The full version uses the **delta method** — a first-order Taylor expansion of the Sharpe ratio around the population *(μ, σ)*. Writing *S* = *μ* / *σ*:

> ∂*S*/∂*μ* = 1/*σ*,    ∂*S*/∂*σ* = −*μ*/*σ*²

Asymptotically, *μ̂* and *σ̂* are independent for normal data, and *Var(σ̂)* ≈ *σ*² / (2*N*). So:

> *Var*(*Ŝ*) ≈ (1/*σ²*) · *σ²*/*N* + (*μ²*/*σ⁴*) · *σ²*/(2*N*) = (1 + *S²*/2) / *N*

> *SE(Ŝ)* ≈ √[(1 + *S²*/2) / *N*]

For typical financial Sharpes (annualized *S* ≈ 0.5, daily *S* ≈ 0.5 / √252 ≈ 0.03), the *S²*/2 term is negligible (~0.0005) and the simple "σ-known" approximation is essentially correct. For high-Sharpe strategies (annualized *S* > 1, daily *S* approaching 0.1), the correction term is non-trivial. The *normal-returns* assumption underlying the delta-method derivation is also approximate — bootstrap is the more honest CI for fat-tailed financial returns, and the §7 stretch exercise asks you to compare.

</details>

### 4.4 What this means with $100k

Two managers, both with 20-year track records. Manager A: point Sharpe 0.45. Manager B: point Sharpe 0.65.

- **Naive read:** Manager B is meaningfully better. Pay them more.
- **Honest read:** Their CIs overlap. You cannot reject "they're equivalent and the difference is luck" at standard confidence levels.

This is *the* practitioner-grade application of Ch4's lesson. It's also why Sharpe-based hiring/firing decisions on short track records are typically noise.

### 4.5 Sharpe's well-known shortcomings (briefly)

Sharpe is the simplest risk-adjusted-return metric, not the only one. Three shortcomings worth flagging:

1. **Symmetric risk treatment.** Sharpe penalizes upside vol the same as downside vol — a strategy that's wildly volatile up but never loses money looks bad by Sharpe. The **Sortino ratio** uses downside-only deviation in the denominator. *(Named only — full treatment deferred.)*
2. **Vol ≠ all risk.** A strategy with a respectable Sharpe can still spend years in drawdown (§2). The **Calmar ratio** divides annualized return by absolute MDD instead. *(Named only.)*
3. **Manipulable.** Sharpe can be juiced by smoothing returns (illiquid assets that mark to model rather than market) or selling tail risk (covered calls boost Sharpe by truncating the right tail and charging premium). The metric isn't robust to either.

Use Sharpe as the *first* number, not the last word. Pair with drawdown (§2), tail metrics (§3), and skepticism (§4.3).

## 5. What we just learned — three risk metrics, one caution

Organized by flavor (the same taxonomy from §0):

- **Path risk — drawdown.** SPY's GFC drawdown reached −55.2% with a peak-to-recovery span of nearly five years; COVID was −33.7% with months. Path risk has two coordinates (depth *and* duration), not one. Vol alone misses both. **Pays Ch1's "we'll formalize later" debt.**
- **Tail risk — VaR and CVaR.** The fat-tail premium is *quantile-dependent*: at 5% the Gaussian and historical estimates are essentially equal (ratio 0.92); at 1% Gaussian underestimates by ~30% (ratio 1.30); at 0.5% by ~50%. Fat tails are a divergence in *shape* in the deep tail, not a uniform multiplier. CVaR captures shape past the threshold; VaR alone doesn't.
- **Risk-adjusted return — Sharpe.** Defined on excess returns, annualizes by × √252. The 60/40 Sharpe (0.524) edges out equal-weight-8 (0.477) — continuity with Ch3. **Honest CIs on Sharpe overlap heavily** — at 20 years SPY's CI is [0.013, 0.891], so even point-Sharpe differences of 0.4 are borderline indistinguishable. **Pays Ch3's promise; integrates Ch4's noise lesson.**

The connecting thread: every one of these metrics carries hidden information beyond the headline number — drawdown's recovery time, VaR's tail shape (especially how the Gaussian/historical gap evolves with α), Sharpe's CI width. Reporting only the scalar throws that information away. Pair the headline with at least one secondary characterization.

## 6. So what?

**Decision rules this chapter unlocks:**

- *Use drawdown for position sizing, not vol.* "Can I sit through −55% over five years on this position?" is the holding question, not "can I sit through one bad day."
- *Match the VaR method to the quantile.* For shallow tails (5%), parametric Gaussian is fine. For deep tails (1% and beyond), use historical — that's where the fat-tail premium materially bites.
- *Pair VaR with CVaR.* VaR alone hides tail shape. CVaR ≥ VaR always; the gap is information about how bad the worst breaches get. Notably, the 5% CVaR sits in the deep-tail region where Gaussian fails, even when 5% VaR doesn't.
- *Compare Sharpes only with their CIs.* A 0.2 difference at 20 years is plausibly noise. Sharpe inherits the noise of its numerator; Ch4 measured how much that is.
- *Use rolling r<sub>f</sub>, not a single constant.* The 20y window spans ZIRP (~0%) and 5% rate regimes. A constant assumption distorts entire subperiods.

**What this chapter can't yet tell you:**

- *How to forecast drawdown / VaR forward (regime-conditional).* → Ch9 (GARCH).
- *How to model tail behavior beyond what's been seen historically.* → Ch10 (EVT, generalized Pareto).
- *How to actually build the portfolio whose Sharpe you'd want to maximize.* → Ch6.
- *Whether a high Sharpe survives transaction costs and slippage.* → Ch13–14.

## 7. Up next

**Chapter 6 — Portfolio Construction: Efficient Frontier and Risk Parity.** Markowitz mean-variance optimization, the **efficient frontier**, the **tangency portfolio** (the one with maximum Sharpe — Ch5's metric becomes Ch6's optimization objective), and **risk parity** as the practitioner's answer to mean-variance instability. Ch4's shrinkage feeds in as the input that keeps the optimization stable; Ch5's Sharpe is what it's optimizing.

## Key Terms

| Term | Brief meaning |
|---|---|
| Drawdown | Current price as a fraction below the running peak. Always ≤ 0 in our convention. |
| Running peak | The maximum price observed up to and including time *t*. |
| Max drawdown (MDD) | The worst (most negative) drawdown over a window. |
| Underwater curve | Time-series plot of drawdown — visualizes "submerged" periods. |
| Recovery time | Days between the peak preceding a drawdown and the first new peak after. |
| Value at Risk (VaR) | A threshold loss; the α-quantile of the loss distribution, sign-flipped to a positive loss. |
| Confidence level (α) | The tail probability VaR refers to — e.g., 5% means worst-5% threshold. |
| Historical VaR | VaR computed empirically from the sample, no distributional assumption. |
| Parametric (Gaussian) VaR | VaR computed assuming returns are normal. Fine at conventional 5% levels; underestimates deep in the tail. |
| Tail premium | The gap between historical and parametric VaR; *quantile-dependent* — appears in the deep tail, not at conventional confidence levels. |
| Conditional VaR (CVaR) | Expected loss *given* that the loss exceeds the VaR threshold. ≥ VaR by construction. |
| Expected Shortfall (ES) | Synonym for CVaR. |
| Risk-free rate (*r<sub>f</sub>*) | Yield on a (effectively) zero-default-risk asset; T-bill yield in practice. |
| T-bill | Short-term US Treasury debt; the standard *r<sub>f</sub>* proxy. |
| ZIRP | Zero-interest-rate-policy era when *r<sub>f</sub>* sat near 0%. |
| Excess return | Asset return minus risk-free rate; compensation for taking risk. |
| Sharpe ratio | Mean excess return divided by excess-return volatility. The simplest risk-adjusted-return metric. |
| Annualized Sharpe | Sharpe scaled by √252 (not 252) for daily data. |
| Sortino ratio | (named only) Sharpe variant penalizing only downside vol. |
| Calmar ratio | (named only) Annualized return divided by absolute MDD. |
| Delta method | First-order-Taylor approximation used to derive *SE(Sharpe)* from *SE(μ)* and *SE(σ)*. |

## Exercises

1. **Different ticker drawdown.** Re-compute MDD and recovery time for **TLT** over the same 20y window. TLT's worst drawdown likely arrived in 2022 (rates regime change — the Fed hiked aggressively to fight inflation, which directly hurt long-duration bonds). Compare its depth and recovery dynamics to SPY's 2008. Are they comparable in depth? In duration? What does that tell you about long-duration Treasuries as a risk-management tool?

2. **Deep-tail VaR.** Compute SPY's 0.5% historical VaR and 0.5% Gaussian VaR. The chapter showed that the historical/Gaussian ratio grows from 0.92 (5%) to 1.30 (1%); does it continue growing at 0.5%? Now repeat the comparison on **GLD** instead of SPY — does gold show a similar tail-premium pattern, or a different one? (Hint: gold has well-documented one-way large-positive-return days that don't correspond to the equity tail.)

3. **Sharpe of Ch3 portfolios with full CI on a shorter window.** Repeat §4.3's CI exercise for the **60/40** and **equal-weight-8** portfolios using only the most recent **5 years** of data instead of 20. How much wider are the CIs? Is *any* pair of Sharpes statistically distinguishable at 5 years?

4. *(stretch)* **Bootstrap Sharpe.** Resample SPY's 20y daily returns with replacement, using a **block-bootstrap** of length 21 days (preserves some volatility clustering — naive iid bootstrap would smear it out). Compute Sharpe on each resample; build a 95% CI from the bootstrap distribution. Compare to the analytic CI from §4.3 ([0.013, 0.891]). Is the analytic CI conservative (wider) or aggressive (narrower)? Why might that be? Hint: the analytic CI assumes independent normal returns; financial returns are neither.
