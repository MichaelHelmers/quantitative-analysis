# Chapter 2 — Risk: Volatility Clustering and Fat Tails

> **Goal of this chapter:** show — empirically, with the same kinds of plots Chapter 1 used — that real daily returns violate two assumptions Chapter 1 quietly leaned on:
> 1. Returns are **i.i.d.** (independent and identically distributed across days).
> 2. Returns are **roughly normally distributed**.
>
> Both are useful starting points; both are wrong in specific, consequential ways. Chapter 2 makes the breaks concrete.

To study rare events we need a longer history than Chapter 1's 5-year window — five years isn't enough trading days to see a real crisis. This chapter pulls **20 years** of SPY data, capturing the 2008 financial crisis, the 2020 COVID crash, and several smaller regimes in between.

We split the chapter in two halves. Part I attacks the *normal* assumption (the **fat-tails** finding). Part II attacks the *i.i.d.* assumption (the **volatility clustering** finding). The order is pedagogical, not chronological — fat tails reuse Chapter 1's tools almost unchanged, while clustering needs new computational machinery (rolling windows, autocorrelation).

---

## What we mean by "risk"

Chapter 1 collapsed risk into a single number — σ, the standard deviation of returns — and used "risk" and "volatility" interchangeably. That's a useful starting point but a misleading stopping point: it quietly claims three things, all of which are wrong in ways that matter.

1. **Risk is one number.** In reality, risk has several distinct flavors that don't reduce to each other:
   - **Magnitude risk** — how bad can a *single* day be?
   - **Persistence risk** — once things get bad, how long do they stay bad?
   - **Path / drawdown risk** — what's the worst peak-to-trough loss the position racks up *across many days*?
   - **Correlation risk** — when one position blows up, do the other positions you held to "diversify" blow up alongside it?
2. **Risk is constant over time.** A single σ implies that next month looks statistically like last month.
3. **Risk is well-described by a bell curve.** The √t rule, "X-σ events," and most introductory finance lean on this.

Chapter 2 attacks #2 and #3 head-on with two empirical findings about real returns: **fat tails** (the bell curve underestimates the worst days) and **volatility clustering** (σ has memory; calm and storm each persist). Together, these are the chapter's account of **magnitude risk** and **persistence risk**.

The other two flavors are real and central — they just aren't this chapter:
- **Drawdown / path risk** lands in a future risk-metrics chapter (alongside VaR, Sharpe), promised since Chapter 1.
- **Correlation risk** is the entire subject of Chapter 3.

When the rest of this chapter says "risk," read it as "the magnitude and persistence dimensions of risk" — not "everything anyone has ever called risk."

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

The eyeball test is convincing but informal. The standard quantitative measure of how heavy a distribution's tails are is **kurtosis**.

Before stating the formula, one piece of notation we'll use through the rest of the chapter:

> **Expected value**, written *E*[·] — the average of whatever is in the brackets, taken over the data. For a sample of *n* observations, *E*[*x*] = (*x*<sub>1</sub> + *x*<sub>2</sub> + … + *x<sub>n</sub>*) / *n* — the same operation as the **mean** (Chapter 1 §4). The bracket notation just lets us write the average of a more complex expression cleanly: *E*[(*X* − *μ*)²] reads as "the mean of the squared deviations," *E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)] as "the mean of the product of two variables' deviations," and so on.

With that in hand:

> *K* = *E*[(*r* − *μ*)⁴] / *σ*⁴

where:
- *r* — a single observation (here, one day's log return).
- *μ* — the mean of the distribution.
- *σ* — the standard deviation.

In plain English: kurtosis is the **mean of the fourth powers of deviations**, divided by *σ*⁴ to make it scale-free. The fourth-power weighting is what makes it sensitive to extreme observations — a single 8σ day contributes 8⁴ = 4096 times more to the average than a typical 1σ day.

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

### 2.5 What this means in dollars (magnitude risk, made concrete)

Kurtosis ≈ 14 and "|z| > 5 happens several times in 20 years" are abstract. The same finding in dollars:

- SPY's **worst single day** in this 20-year window is roughly **−10.9%** (March 16, 2020). Under a normal model fit to the same data, a day that bad has probability ≈ 10⁻¹⁹ — not "once in a century" but "once in a billion times the age of the universe." The normal model isn't *a little* off in the tail; it's not in the same conceptual neighborhood as reality.
- On a **$100,000 SPY position** that day, the actual loss was ~$10,900. A normal-distribution Value-at-Risk report run the night before would have flagged any loss above ~$3,500 as a once-in-a-century event. The realized loss was ~3× that "once-in-a-century" line.
- 2008's worst day (−9.0%, Oct 15) and 1987's Black Monday (−20.5%) tell the same story.

This is what **magnitude risk** is, concretely: not "kurtosis is high" but "*the single-day worst case you'll experience is several times larger than a bell-curve risk model says it is.*" The fat-tails finding is the chapter's way of seeing magnitude risk for what it actually is.

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

The rolling-vol plot is suggestive: high-vol days seem to follow high-vol days. The formal version of "follows" is **autocorrelation**. Two supporting definitions first — both built from the *E*[·] notation we introduced in §2.2:

> - **Covariance** of two series *X* and *Y* — Cov(*X*, *Y*) = *E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)]. In words: for each paired observation, take *X*'s deviation from its mean and *Y*'s deviation from its mean, multiply them, then take the **mean** of all those products. Positive when *X* and *Y* tend to be above/below their means *together*, negative when they move oppositely, zero when independent.
> - **Variance** (recap from Chapter 1) — the **mean of the squared deviations from the mean**: Var(*X*) = *E*[(*X* − *μ*)²]. A special case of covariance: Var(*X*) = Cov(*X*, *X*).

Now the autocorrelation:

> *ρ<sub>k</sub>* = Cov(*X<sub>t</sub>*, *X<sub>t−k</sub>*) / Var(*X<sub>t</sub>*)

where:
- *X<sub>t</sub>* — value of some series at time *t* (here, daily returns or |returns|).
- *X<sub>t−k</sub>* — the same series shifted *k* periods backward.
- *k* — the **lag** (number of periods of separation; *k* = 1 is "yesterday vs today").
- Cov(*X<sub>t</sub>*, *X<sub>t−k</sub>*) — the covariance between today's value and the value *k* days ago, computed across all valid *t* pairs in the series.
- Var(*X<sub>t</sub>*) — the variance of the series. Dividing by it scales the result so that *ρ<sub>k</sub>* is unitless.
- *ρ<sub>k</sub>* ranges from −1 (perfect anti-correlation) to +1 (perfect correlation); 0 means independent.

We compute autocorrelation two ways:

1. **On returns themselves**, *r<sub>t</sub>* — answers "is today's return predictable from yesterday's?"
2. **On absolute returns**, |*r<sub>t</sub>*| — answers "is today's *magnitude* predictable from yesterday's?"

The two side-by-side bar charts in the notebook show the contrast cleanly. Returns are essentially uncorrelated at every lag — the textbook "markets are unpredictable" finding. Absolute returns are clearly positively autocorrelated, slowly decaying out to many lags.

That gap **is** volatility clustering: the **second moment** of returns (magnitude, variance) exhibits memory; the **first moment** (signed return) does not. Almost every quantitative risk model — **GARCH** being the most famous — exists to model this asymmetry.

### 3.3 What this means as an investor (persistence risk, made concrete)

Two investors who each hold the **same $100,000 SPY position** experience radically different lives depending on which regime they're in.

- **June 2017**, rolling 21-day vol ≈ **7%** annualized → daily std ≈ 0.4%. A typical day is ±$400; a "rough" day might be −$1,000. You barely notice the position day to day.
- **March 2020**, rolling 21-day vol ≈ **80%** annualized → daily std ≈ 5%. A typical day is ±$5,000; the worst day was −$10,900. You notice the position every five minutes.

Same nominal exposure. More than 10× the day-to-day pain. That's **persistence risk** — also called *regime risk*. The single 19% annualized number from Chapter 1 is the *average* across these wildly different stretches; it is *not* a description of what any individual stretch of holding the asset actually feels like.

Why the word "persistence": the autocorrelation finding tells you these regimes are *sticky*. A calm last month very probably means a calm next week; a wild last month very probably means a wild next week. The danger isn't that one bad day happens — it's that bad days *cluster into stretches* where the worst-case-of-the-stretch is far worse than the worst-case-of-any-given-day.

### A note on stationarity

A series is **stationary** when its statistical properties don't change over time. Returns are *approximately* mean-stationary (the long-run mean drifts slowly), but they are clearly *not* variance-stationary — the rolling-vol plot is the proof. A different way to state Chapter 2's findings: SPY's daily returns are non-stationary in their second moment, and the regime they're currently in carries information about the regime they'll be in tomorrow. That's a long way from i.i.d.

## 4. What we just learned — and what risk actually is

Chapter 1's working definition was *risk = volatility = σ*. Chapter 2 has expanded that into something more honest. The two empirical findings map cleanly onto two distinct flavors of risk that the single-σ picture conflated:

- **Magnitude risk — captured by *fat tails*.** The single-day worst case is bigger than a bell curve admits, by orders of magnitude in the deep tail. Excess kurtosis well above zero, Q-Q tails bending off the diagonal, observed |z|>5 days where the normal model expects approximately zero, and a real $100k SPY position losing ~$10,900 on a day a normal-distribution risk report would have called once-in-a-century. *Where this matters:* option pricing models that assume normality (Black–Scholes) systematically underprice deep out-of-the-money options; Value-at-Risk computed under normal assumptions is too optimistic about crash risk.
- **Persistence risk — captured by *volatility clustering*.** σ is itself a moving target. Rolling vol swings between ~10% and ~80%; positive autocorrelation in |returns| persists out to many lags. The lived experience of holding the asset varies by 10× depending on which regime you're in. *Where this matters:* the single annualized-vol number from Chapter 1 is an average over genuinely different regimes; risk models and position-sizing rules that assume vol is constant miss most of the action.

Two flavors of risk that we *haven't* yet covered, and that you should know are missing:

- **Drawdown / path risk** — peak-to-trough damage compounding across many days. SPY's max drawdown in this window is roughly **−55%** (peak Oct 2007 → trough Mar 2009), which a one-day-at-a-time view never sees. Owed from Chapter 1; lands in a future risk-metrics chapter alongside VaR.
- **Correlation risk** — when "diversifiers" fail you. Comes up the moment we hold more than one asset, which is Chapter 3's territory.

Both of this chapter's findings have formal modeling tools we'll meet later in the guide:
- **GARCH** (Generalized AutoRegressive Conditional Heteroskedasticity) — the workhorse model for time-varying volatility. Models conditional variance as a function of recent shocks and recent variance, directly capturing the clustering pattern.
- **EVT / generalized Pareto distributions** — the standard family for modeling tail behavior beyond the normal model, used in operational risk and insurance.

Neither is required for everyday return analysis; both are worth knowing about.

---

## So what? — decisions this chapter lets you make

Chapter 1 gave you a single vol number and a normal-distribution mental model. Chapter 2 broke both. Here's what to actually *do* with the broken pieces:

- **Discount any "X-sigma event" claim by orders of magnitude.** When a risk report or news article calls something "a 5σ move — should happen once in 14,000 years," translate it as "happens a few times per decade in this asset." The fat-tail count table is the receipt. Practically: if a strategy's worst-case scenarios are computed under a normal assumption, assume the real worst case is meaningfully worse.
- **Don't size positions off long-run volatility — use a recent window.** Chapter 1's vol-targeting rule (target ÷ σ) only works if σ reflects *current* conditions. The rolling-vol plot shows σ swinging between ~10% and ~80%. A reasonable default is to size off **N = 21-day** (≈ one month) realized vol, refreshed daily. Long windows (N ≥ 63) lag the regime; very short windows (N ≤ 5) jitter too much to size off.
- **After a shock, expect more shock.** Volatility clustering is the formal version of "the market is jumpy right now." If today's |z| > 3, tomorrow's vol is statistically likely to be elevated — that is exactly what positive autocorrelation in |returns| means. The simplest decision rule: after a large-magnitude day, *reduce* gross exposure until rolling vol comes back down. The opposite mistake — "vol is back to normal because yesterday was calm" — ignores the slow autocorrelation decay.
- **Don't expect that rule to predict direction.** The autocorrelation of *signed* returns is essentially zero. Clustering tells you the *size* of tomorrow's move is forecastable; the *sign* isn't. Anyone selling a "the market will drop tomorrow" forecast based on yesterday's drop is selling something the data doesn't support.
- **Use Q-Q plots as a fast sanity check on any return series.** Five seconds of looking at a Q-Q plot tells you whether a model that assumes normality is going to embarrass you in this regime. If both ends bend off the diagonal, normality-based risk numbers are not safe.

What this chapter *can't* yet tell you: how to combine these effects across multiple assets at once (Chapter 3, correlation), or how to turn "elevated vol" into a single number that summarizes "how bad could a day actually be" (the eventual VaR / max-drawdown chapter).

---

## Key Terms (Chapter 2)

| Term | Meaning | First used |
|------|---------|-----------:|
| Magnitude risk | How bad a *single* day can be; the dimension of risk fat tails make visible | "What we mean by risk" |
| Persistence risk | How long bad conditions stay bad; the dimension clustering makes visible | "What we mean by risk" |
| Drawdown / path risk | Peak-to-trough damage compounded across many days (deferred) | "What we mean by risk" |
| Correlation risk | Whether "diversifying" positions actually move independently (deferred to Ch3) | "What we mean by risk" |
| Fat tails | Tails heavier than a normal distribution would predict | §2 |
| Expected value (*E*[·]) | The mean of the bracketed expression; same operation as *mean*, but with notation that nests | §2.2 |
| Kurtosis (*K*) | *E*[(*r* − *μ*)⁴] / *σ*⁴; a measure of tail weight | §2.2 |
| Excess kurtosis | *K* − 3; positive means fatter-tailed than a normal | §2.2 |
| Leptokurtic | Technical term for "fat-tailed" (excess kurtosis > 0) | §2.2 |
| Quantile | The *p*-th quantile is the value below which fraction *p* of the data falls | §2.3 |
| Median / quartile | The 0.5 quantile / the 0.25 and 0.75 quantiles | §2.3 |
| Q-Q plot | Quantile-quantile plot; visual diagnostic comparing distributions | §2.3 |
| z-score | (*r* − *μ*) / *σ*; number of std deviations from the mean | §2.4 |
| Volatility clustering | Empirical finding that vol persists — high follows high, low follows low | §3 |
| Rolling window | A sliding subset of a time series used to compute statistics at each point | §3.1 |
| Window length (*N*) | Number of observations in a rolling window | §3.1 |
| Covariance | Cov(*X*, *Y*) = *E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)]; mean of the product of deviations | §3.2 |
| Autocorrelation (*ρ<sub>k</sub>*) | Correlation of a series with a lagged version of itself | §3.2 |
| Autocovariance | Covariance of a series with a lagged version of itself; numerator of *ρ<sub>k</sub>* | §3.2 |
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
