# Chapter 2 — Risk: Volatility Clustering and Fat Tails

> **Goal of this chapter:** show — empirically, with the same kinds of plots Chapter 1 used — that real daily returns violate two assumptions Chapter 1 quietly leaned on:
> 1. Returns are **i.i.d.** (independent and identically distributed across days).
> 2. Returns are **roughly normally distributed**.
>
> Both are useful starting points; both are wrong in specific, consequential ways. Chapter 2 makes the breaks concrete.

To study rare events we need a longer history than Chapter 1's 5-year window — five years isn't enough trading days to see a real crisis. This chapter pulls **20 years** of SPY data, capturing the 2008 financial crisis, the 2020 COVID crash, and several smaller regimes in between.

We split the chapter in two halves. Part I attacks the *normal* assumption (the **fat-tails** finding). Part II attacks the *i.i.d.* assumption (the **volatility clustering** finding). The order is pedagogical, not chronological — fat tails reuse Chapter 1's tools almost unchanged, while clustering needs new computational machinery (rolling windows, autocorrelation).

---

## 1. Setup

We use the same library stack as Chapter 1 plus `scipy.stats` for the fitted-normal density and the Q-Q plot. Log returns are the primary series throughout — the math and statistical arguments coming up work cleaner with logs (Chapter 1 §2 covered the simple-vs-log distinction).

Expect to see, after the setup cells run:
- **~5,030 daily observations** spanning ~20 years.
- **daily mean** ≈ 0.0004, **daily std** ≈ 0.012.
- **annualized volatility** ≈ 19% (right in the middle of the 15–25% range Chapter 1 said was typical for an equity index).

## 2. Part I — The histogram lies (fat tails)

Chapter 1 §5 said in passing that the daily-return histogram had "a few outliers in the ±3% to ±5% range — those are the **fat tails**." We're going to make that precise now: how *much* fatter than the normal-distribution model predicts? Three independent ways to answer it: by eye (overlay), by number (kurtosis), and by counting (tail probabilities).

### 2.1 The bell curve doesn't fit the tails

Re-plot the daily-return histogram from Chapter 1, but overlay the **normal density** *N*(*μ*, *σ*²) using the empirical mean and standard deviation. If returns were truly normal, the histogram and the curve should match.

> *N*(*x*; *μ*, *σ*) = (1 / (*σ* √(2π))) · exp(−(*x* − *μ*)² / (2*σ*²))
>
> where:
> - *x* — the value the density is evaluated at (a daily return).
> - *μ*, *σ* — mean and standard deviation, taken from the data.

The plot uses a **log y-axis** because on a linear axis the tail bars are too small to see. On the log axis, the gap is glaring: the histogram bars in both tails sit far above the red curve.

### 2.2 Kurtosis — putting a number on "fat-tailedness"

The eyeball test is convincing but informal. The standard quantitative measure of how heavy a distribution's tails are is **kurtosis**:

> *K* = E[(*r* − *μ*)⁴] / *σ*⁴

where:
- *r* — a single observation (here, one day's log return).
- *μ* — the mean of the distribution.
- *σ* — the standard deviation.
- *E*[·] — the **expected value** (population mean of the bracketed quantity).

For a **normal distribution**, *K* = 3. By convention we usually report **excess kurtosis**, *K* − 3, so that "0" means "as fat-tailed as a normal" and positive numbers mean fatter. A distribution with positive excess kurtosis is called **leptokurtic**.

<details>
<summary><b>The math, if you want it: why <i>K</i> = 3 for a normal distribution</b></summary>

For a standard normal *Z* ~ *N*(0, 1), the moments are computed by integration against the density. The fourth moment is:

> E[*Z*⁴] = ∫<sub>−∞</sub><sup>∞</sup> *z*⁴ · (1 / √(2π)) · *e*<sup>−*z*²/2</sup> *dz* = 3

This is a standard Gaussian-moment result — for a standard normal, *E*[*Z*<sup>2*n*</sup>] = (2*n* − 1)!! (the double factorial), which gives 1, 3, 15, 105, … for *n* = 1, 2, 3, 4. Since *σ* = 1 for a standard normal, the kurtosis E[*Z*⁴] / *σ*⁴ = 3 / 1 = 3. Standardization (*r* → (*r* − *μ*) / *σ*) means the same answer applies to *any* normal, not just the standard one.

The "subtract 3" convention exists precisely so that any distribution can be compared against the normal benchmark just by checking the sign of *K* − 3.

</details>

For SPY's 20 years of daily log returns, expect excess kurtosis well into the double digits — typically **10–15**. That's huge. Most equity indices land in the 4–15 range over multi-decade windows; individual stocks and crypto routinely land higher.

> **Aside on interpretation:** kurtosis is dominated by the *fourth power* of deviations, so a single 8σ day will swing the statistic substantially. That's a feature, not a bug — kurtosis is *trying* to be sensitive to extremes.

### 2.3 Q-Q plot — visual second confirmation

> **Quantile** — a cut-point along a distribution. The *p*-th quantile is the value below which a fraction *p* of the data falls. The 0.5 quantile is the **median**; the 0.25 and 0.75 quantiles are the first and third **quartiles**; the 0.99 quantile is "the value 99% of the observations are below." A distribution is fully described by listing all of its quantiles.

A **Q-Q plot** (quantile–quantile plot) is a visual diagnostic that compares two distributions by plotting their quantiles against each other. For each fraction *p* (e.g., *p* = 0.05, 0.10, 0.50, 0.90, 0.95, …), find the *p*-th quantile of the empirical data on one axis and the *p*-th quantile of a reference distribution (here, the normal) on the other. If the two distributions match, the points lie on the 45° identity line.

For SPY's daily returns the points trace the line in the middle (the bulk of the data is approximately normal), but bend *away* from it at both ends — the right tail bends up (the empirical 99th-quantile return is *larger* than the normal would predict), the left tail bends down (the empirical 1st-quantile return is *more negative* than the normal would predict). That banana shape is the visual fingerprint of fat tails.

### 2.4 Counting tail days — the rhetorical payoff

The most convincing form of the same fact is to count: under a normal model with SPY's empirical *μ* and *σ*, how often *should* extreme days happen, and how often *do* they?

Define the **z-score**:

> *z<sub>t</sub>* = (*r<sub>t</sub>* − *μ*) / *σ*

where:
- *r<sub>t</sub>* — the day's return.
- *μ*, *σ* — sample mean and standard deviation.
- *z<sub>t</sub>* — number of standard deviations the day is from the mean.

Predicted frequencies under a normal model:

| Threshold | Expected % | Roughly… |
| --- | --- | --- |
| \|*z*\| > 2 | 4.55% | ~12 days/year |
| \|*z*\| > 3 | 0.27% | ~1 day every 1.5 years |
| \|*z*\| > 4 | 0.0063% | ~1 day every 64 years |
| \|*z*\| > 5 | 0.000057% | ~1 day every 14,000 years |

The notebook computes the corresponding *observed* counts in 20 years of SPY. The first row will roughly match (the model gets the bulk right). By |*z*| > 4, the data has dozens of days where the model expects fractions of one. By |*z*| > 5 — "should never happen in human history" — there are several.

This is the same story kurtosis told us, in a form that's hard to ignore: **risk models that assume normal-distributed returns systematically underweight rare disasters.** That's the punchline of Part I.

## 3. Part II — Volatility isn't constant (clustering)

Part I showed the **distribution shape** of daily returns isn't normal. Part II shows something different but equally important: even the *parameters* of that distribution change over time. Specifically the standard deviation — the volatility — is itself a moving target. Quiet periods follow quiet periods; stormy periods follow stormy periods. This phenomenon has a name: **volatility clustering**.

### 3.1 Rolling-window volatility

If we want to see how vol changes through time, we can compute the standard deviation over a **rolling window** — a sliding subset of the time series. At each date *t*, take the last *N* days of returns, compute their standard deviation, and annualize:

> *σ<sub>t</sub>*<sup>(N)</sup> = std(*r<sub>t−N+1</sub>*, …, *r<sub>t</sub>*) × √252

where:
- *N* — the **window length** in trading days. Common choices: 21 (≈ one trading month), 63 (≈ one quarter).
- *r<sub>t−N+1</sub>*, …, *r<sub>t</sub>* — the *N* most recent daily returns at time *t*.
- The √252 factor is the same annualization rule from Chapter 1 §4.

The notebook plots this with *N* = 21. The single full-sample number from Chapter 1 (~19%) becomes a dashed line — useful as a summary, but the rolling line tells a richer story:

- **2008–2009** — vol explodes during the financial crisis, sustained for ~12 months at 50%+.
- **2010–2014** — gradually elevated, with the August 2011 European-debt spike clearly visible.
- **2015–2019** — generally calm, occasionally interrupted (Aug 2015, Feb 2018 — "vol-mageddon").
- **March 2020** — the COVID spike, briefly peaking above 80%.
- **2022** — sustained elevated vol during the rate-hike correction.

The notebook also overlays *N* = 5, 21, 63 on the same axes. The 5-day version reacts quickly but is jittery; 63-day is smooth but lags by ~3 months. There's no canonical "right" window — the choice depends on what the vol estimate is being used for.

### 3.2 Autocorrelation — the formal statement of clustering

The rolling-vol plot is suggestive: high-vol days seem to follow high-vol days. The formal version of "follows" is **autocorrelation**.

> *ρ<sub>k</sub>* = Cov(*X<sub>t</sub>*, *X<sub>t−k</sub>*) / Var(*X<sub>t</sub>*)

where:
- *X<sub>t</sub>* — value of some series at time *t*.
- *k* — the **lag** (number of periods of separation; *k* = 1 is "yesterday vs today").
- *ρ<sub>k</sub>* ranges from −1 (perfect anti-correlation) to +1 (perfect correlation); 0 means independent.

We compute autocorrelation two ways:

1. **On returns themselves**, *r<sub>t</sub>* — answers "is today's return predictable from yesterday's?"
2. **On absolute returns**, |*r<sub>t</sub>*| — answers "is today's *magnitude* predictable from yesterday's?"

The two side-by-side bar charts in the notebook show the contrast cleanly. Returns are essentially uncorrelated at every lag — the textbook "markets are unpredictable" finding. Absolute returns are clearly positively autocorrelated, slowly decaying out to many lags.

That gap **is** volatility clustering: the **second moment** of returns (magnitude, variance) exhibits memory; the **first moment** (signed return) does not. Almost every quantitative risk model — **GARCH** being the most famous — exists to model this asymmetry.

### A note on stationarity

A series is **stationary** when its statistical properties don't change over time. Returns are *approximately* mean-stationary (the long-run mean drifts slowly), but they are clearly *not* variance-stationary — the rolling-vol plot is the proof. A different way to state Chapter 2's findings: SPY's daily returns are non-stationary in their second moment, and the regime they're currently in carries information about the regime they'll be in tomorrow. That's a long way from i.i.d.

## 4. What we just learned

Two empirical facts that quietly invalidate the i.i.d.-normal model from Chapter 1:

- **Fat tails.** Excess kurtosis well above zero, Q-Q plot tails bending away from the diagonal, and a tail-count table showing the normal model under-predicts extreme days by orders of magnitude. **Where this matters:** option pricing models that assume normality (Black–Scholes) systematically underprice deep out-of-the-money options; Value-at-Risk computed under normal assumptions is too optimistic about crash risk.
- **Volatility clustering.** Rolling vol that swings between ~10% and ~80%; positive autocorrelation in |returns| out to many lags. **Where this matters:** the single annualized-vol number from Chapter 1 is a rough average over genuinely different regimes. Risk models that assume vol is constant (the Chapter 1 √t rule, applied naively) miss most of the action.

Both findings have formal modeling tools that we'll meet later in the guide:
- **GARCH** (Generalized AutoRegressive Conditional Heteroskedasticity) — the workhorse model for time-varying volatility. Models the conditional variance as a function of recent shocks and recent variance, which directly captures the clustering pattern.
- **EVT / generalized Pareto distributions** — the standard family for modeling tail behavior beyond the normal model, used in operational risk and insurance.

Neither is required for everyday return analysis; both are worth knowing about.

---

## Key Terms (Chapter 2)

| Term | Meaning | First used |
|------|---------|-----------:|
| Fat tails | Tails heavier than a normal distribution would predict | §2 |
| Kurtosis (*K*) | E[(*r* − *μ*)⁴] / *σ*⁴; a measure of tail weight | §2.2 |
| Excess kurtosis | *K* − 3; positive means fatter-tailed than a normal | §2.2 |
| Leptokurtic | Technical term for "fat-tailed" (excess kurtosis > 0) | §2.2 |
| Quantile | The *p*-th quantile is the value below which fraction *p* of the data falls | §2.3 |
| Median / quartile | The 0.5 quantile / the 0.25 and 0.75 quantiles | §2.3 |
| Q-Q plot | Quantile-quantile plot; visual diagnostic comparing distributions | §2.3 |
| z-score | (*r* − *μ*) / *σ*; number of std deviations from the mean | §2.4 |
| Volatility clustering | Empirical finding that vol persists — high follows high, low follows low | §3 |
| Rolling window | A sliding subset of a time series used to compute statistics at each point | §3.1 |
| Window length (*N*) | Number of observations in a rolling window | §3.1 |
| Autocorrelation (*ρ<sub>k</sub>*) | Correlation of a series with a lagged version of itself | §3.2 |
| Lag (*k*) | Number of periods by which a series is shifted | §3.2 |
| First / second moment | Mean (1st) and variance (2nd) of a distribution | §3.2 |
| Stationarity | Statistical properties don't change over time | §3 (note) |
| Regime | A persistent macro-state with characteristic statistical properties | §3.1 |
| GARCH | Family of models for time-varying volatility (deferred) | §4 |
| EVT | Extreme value theory; models for tail behavior (deferred) | §4 |

---

## Exercises

Try these in fresh cells at the bottom of the notebook:

1. **Different ticker.** Re-run the chapter with `AAPL` or with `BTC-USD`. Is the excess kurtosis higher or lower than SPY's? How does the rolling-vol pattern compare — same spikes in the same places, or different?
2. **Calmest vs stormiest year.** Find SPY's calmest 252-day window (lowest realized vol) and stormiest. Compute kurtosis on each. Does the *shape* of the distribution change with the regime, or just its width?
3. **Returns² instead of |returns|.** Re-do the right-hand autocorrelation chart using `log_returns ** 2`. Does it look the same? Stronger? Weaker? Why might either be true?
4. *(stretch)* Pull a non-equity ticker — `TLT` (long-dated US Treasuries) or `GLD` (gold). Are these effects (fat tails, clustering) equity-specific, or universal across asset classes?

---

## Up next

**Chapter 3: Multiple assets — correlation and diversification.** We move from one ticker to a basket. The big question: when you combine assets, how do their returns *co-move*, and what does that combination do to portfolio-level risk? Spoiler — sometimes a lot, sometimes almost nothing, and the difference is the entire premise of modern portfolio construction.
