# Chapter 2 — Risk: Volatility Clustering and Fat Tails

**Status:** Design approved 2026-04-25
**Author chapter slot:** `02-risk/`
**Predecessor:** Chapter 1 — Foundations: Prices and Returns (`01-foundations/`)
**Successor (planned):** Chapter 3 — Multiple Assets: Correlation and Diversification

---

## 1. Background and motivation

Chapter 1 derived a small set of summary statistics from a daily price series — most importantly, **annualized volatility** as the standard deviation of returns. Two assumptions were stacked under the √t annualization rule:

1. Daily returns are **i.i.d.** (independent and identically distributed).
2. Daily returns are roughly **normally distributed**.

Both are *useful starting points* and both are *empirically wrong* in specific, consequential ways. Chapter 2 is the chapter that makes those failures concrete:

- The marginal distribution of daily returns has **fat tails** — extreme moves happen far more often than the normal model predicts.
- The variance of daily returns is **not constant over time** — calm periods cluster together, stormy periods cluster together (**volatility clustering**).

Chapter 1 telegraphed this chapter at two points (notebook cell `c8b17957`, README §5 fat-tails gloss, README "Up next"). Chapter 2 cashes those promises.

## 2. Goals and non-goals

### Goals

- Show **fat tails** empirically with one tool the reader already knows (the histogram from Ch1) plus three new ones (normal overlay, kurtosis, Q-Q plot, tail-probability counting).
- Show **volatility clustering** empirically via rolling-window vol time series and the autocorrelation of |returns|.
- Reframe Chapter 1's i.i.d.-normal assumption set in light of both findings, and signal where each break matters in real-world finance (option pricing; static-vol risk management).
- Introduce the new vocabulary the rest of the guide will rely on (*kurtosis*, *Q-Q plot*, *rolling window*, *autocorrelation*, *lag*, *stationarity*, *regime*, *leptokurtic*).

### Non-goals (explicitly deferred)

- **Max drawdown formalization** — promised in Ch1, but better paired with VaR/Sharpe in a future "risk metrics" chapter.
- **Value at Risk (VaR), CVaR, Sharpe ratio** — same chapter as drawdown, after Ch3 establishes portfolio framing.
- **GARCH** — previewed only as "the formal model of clustering"; full treatment is its own chapter.
- **EVT / generalized Pareto** — previewed only.
- **Formal hypothesis tests** (Jarque-Bera, Ljung-Box) — mentioned in one sentence as "the formal statistical versions of these informal observations." No code.
- **Correlation across assets** — that's Chapter 3.

## 3. Narrative arc

The chapter has two halves with a connective tissue paragraph between them:

> Chapter 1 said real returns are roughly i.i.d. and roughly normal — both useful starting points, both wrong in specific ways. This chapter shows the two breaks, in order: first the *normal* assumption fails (Part I, fat tails), then the *i.i.d.* assumption fails (Part II, clustering).

Order rationale: fat tails reuse Ch1's exact tools (histogram + one new line); clustering needs new computational machinery (rolling windows). Pedagogical ramp matters more than the framing-promise made in Ch1's "Up next" — that line will be edited to reflect the actual order.

## 4. Data

- Single ticker: **SPY**.
- History: **20 years** (`yf.download("SPY", period="20y", progress=False)`).
- Use **log returns** as the primary series (Ch1 paid the conceptual cost; the math/stats arguments in Ch2 work cleaner with logs).
- One sentence at the top of the chapter README explains the switch from Ch1's 5y window: *"To study rare events we need a longer window — five years isn't enough to see a real crisis. We use 20 years here, capturing 2008, 2020, and several smaller regimes."*

## 5. Section structure

The notebook and README mirror Chapter 1's six-step rhythm.

### §1. Setup & data refresh

- Imports (`numpy`, `pandas`, `matplotlib`, `yfinance`, `scipy.stats`).
- Pull 20y SPY, derive log returns, brief callback to Ch1's vocabulary (return, log return, volatility).
- Validate: `len(returns)` ≈ 5000.

### §2. Part I — The histogram lies (fat tails / non-normality)

**§2.1 Histogram with normal overlay.** Re-plot Ch1's daily-return histogram, this time overlaying a fitted normal density curve `N(μ, σ²)` using the empirical mean and standard deviation. The visual gap in the tails is the chapter's first hook.

**§2.2 Kurtosis.** Define and compute kurtosis — the formal "fat tails" statistic.

> *K* = E[(*r* − *μ*)⁴] / *σ*⁴; **excess kurtosis** = *K* − 3.

For a normal distribution, *K* = 3 (excess kurtosis = 0). SPY's daily-return distribution will yield excess kurtosis well above zero (typically 10+). Body of the chapter shows the formula and a one-sentence interpretation; collapsible `<details>` block holds the derivation of why a normal distribution gives *K* = 3. Introduce **leptokurtic** as the technical word for "fat-tailed."

**§2.3 Q-Q plot vs normal.** Visual second confirmation. Under perfect normality the points lie on the diagonal; SPY's points will bow away at both ends. Use `scipy.stats.probplot`.

**§2.4 Tail probability table.** Quantitative third confirmation. Compute, side by side:

| Threshold | Predicted by N(μ, σ²) | Observed in SPY (count and %) |
| --- | --- | --- |
| \|*z*\| > 2 | ~4.55% | … |
| \|*z*\| > 3 | ~0.27% | … |
| \|*z*\| > 4 | ~0.0063% | … |
| \|*z*\| > 5 | ~5.7e-5% | … |

The 4σ and 5σ rows are the rhetorical payoff: under normality, a 5σ day should happen roughly once every ~13,900 years; SPY's 20y window will contain several.

### §3. Part II — Volatility isn't constant (clustering)

**§3.1 Rolling-window volatility.** Compute and plot a **rolling 21-day annualized volatility** time series. Visible features in 20y of SPY: 2008 financial-crisis spike, August 2011, August 2015, February 2018 ("vol-mageddon"), March 2020 (COVID), 2022 stretch. Brief paragraph: *why 21 days?* (≈ one trading month — a balance between noise and lag) and *what changes if you pick 5 or 60?* (with one comparison plot showing 5d vs 21d vs 60d on the same axes).

**§3.2 Autocorrelation of |returns|.** Define **autocorrelation** at lag *k*:

> *ρ<sub>k</sub>* = Cov(*r<sub>t</sub>*, *r<sub>t−k</sub>*) / Var(*r<sub>t</sub>*).

Plot two side-by-side bar charts:

- Autocorrelation of **returns themselves** (lags 1–30) — near zero at all lags. Markets aren't directly predictable.
- Autocorrelation of **|returns|** (or returns², either works) — significantly positive at all lags out to 30+. Volatility *is* predictable.

This is the formal statement of clustering: the *sign* of tomorrow's return is unpredictable, but the *magnitude* is not. Introduce **lag**, **stationarity** (briefly — to motivate why constant-vol assumptions are wrong), and **regime**.

### §4. What we just learned

Half-page wrap reframing Ch1's i.i.d.-normal assumption set:

- **Fat tails** → option pricing (Black–Scholes underprices crash risk because it assumes log-normal terminal prices), Value at Risk computed under normal assumptions is too optimistic.
- **Clustering** → static-vol risk management (a single number for "SPY vol = 18%" is misleading; it's been ~10% in calm periods and ~80% in crises). Forecasts of vol must be time-varying.

One paragraph each, no formulas. Sets up GARCH and EVT as named-but-deferred topics.

### §5. Up next

Chapter 3 — **correlation and diversification** (per top-level curriculum). One sentence each on **GARCH** and **EVT** as future-chapter topics for readers who want the formal modeling tools.

### §6. Key Terms table + Exercises

**Key Terms** table covering all new vocabulary from §1–§4 (see §6 of this spec for the full list).

**Exercises** (3–4, Ch1 style):

1. **Different ticker.** Re-run with `AAPL` or `BTC-USD`. Is excess kurtosis higher or lower? Plot rolling vol — are the spikes in the same places as SPY's, or different?
2. **Different window.** Compute kurtosis on the calmest 12-month rolling window vs the stormiest. Does the *distribution shape* change with the regime, or just its width?
3. **|returns|² instead of |returns|.** Re-do the autocorrelation plot using returns². Does it look the same? Stronger? Weaker?
4. *(stretch)* Pull a non-equity ticker (`TLT` for bonds, `GLD` for gold). Does the clustering pattern hold there too?

## 6. New terminology and formulas

### Terms (each gets inline gloss + Key Terms entry + `glossary.md` append)

| Term | Brief meaning |
| --- | --- |
| Kurtosis | A measure of how heavy a distribution's tails are. |
| Excess kurtosis | Kurtosis minus 3 (the kurtosis of a normal distribution). |
| Leptokurtic | Technical word for "fat-tailed" (excess kurtosis > 0). |
| Q-Q plot | Quantile–quantile plot; visual diagnostic comparing two distributions. |
| Rolling window | A sliding subset of a time series used to compute a statistic at each point. |
| Autocorrelation | Correlation of a series with a lagged copy of itself. |
| Lag | The number of periods by which a series is shifted in autocorrelation. |
| Stationarity | A time series whose statistical properties don't change over time. |
| Regime | A persistent macro-state of the market with characteristic statistical properties. |

### Formulas (each gets `where:` symbol legend per convention)

1. **Kurtosis:** *K* = E[(*r* − *μ*)⁴] / *σ*⁴; excess = *K* − 3.
2. **Autocorrelation at lag k:** *ρ<sub>k</sub>* = Cov(*r<sub>t</sub>*, *r<sub>t−k</sub>*) / Var(*r<sub>t</sub>*).
3. **Rolling-window standard deviation:** explicit windowed-sum form so the reader sees what `.rolling(21).std()` is doing under the hood.

Heavier derivations (why *K* = 3 for a normal; the unbiased correction for autocorrelation estimators) live in collapsible `<details>` blocks per the established convention.

## 7. Code structure and dependencies

- `02-risk/README.md` — chapter prose, end-of-chapter Key Terms.
- `02-risk/lesson.ipynb` — runnable notebook with just-in-time micro-explanations per the established pattern.
- Append new entries to root `glossary.md` (alphabetized, tagged Ch. 2).

### New dependencies (update `requirements.txt`)

- `scipy` — for `scipy.stats.norm` (pdf overlay) and `scipy.stats.probplot` (Q-Q).
- *Tentative:* `statsmodels` — only if `pandas.Series.autocorr()` proves insufficient for plotting a clean ACF bar. Default to pandas-only; bring in statsmodels only if needed during implementation.

### No new helpers / no shared module

Each chapter remains self-contained. Re-do the data download in the Ch2 notebook even though Ch1 already pulled SPY — keeps each chapter runnable on its own and matches the Ch1 pattern.

## 8. Conventions to follow

Inherited from prior chapters (see `MEMORY.md` feedback memories):

- Define every domain term on first use (inline blockquote gloss).
- Define every formula symbol via a `where:` legend.
- Inline glosses + chapter Key Terms table + glossary append.
- Notebook cells get just-in-time micro-explanations; deeper "why" lives in the README.
- Heavier math goes in collapsible `<details>` blocks.
- HTML subscripts (`<sub>`) for formula rendering.

## 9. Cross-chapter promises honored

- Ch1 README "Up next" — *"vol clustering as headline empirical fact"* → Part II of this chapter.
- Ch1 notebook `c8b17957` — *"those are the **fat tails** that real-market returns are notorious for, and that Chapter 2 will dwell on"* → Part I of this chapter.
- Ch1 README §4 — *"In real markets returns are not perfectly i.i.d. — Chapter 2 is largely about how they fail this assumption"* → both parts.

## 10. Cross-chapter promises NOT honored (with rationale)

- Ch1 §5 drawdown gloss — *"max drawdown ... we'll formalize later"* → deferred to a future risk-metrics chapter alongside VaR / Sharpe. Will note this in the curriculum-roadmap memory after Ch2 ships.

## 11. Edits required to existing files (Ch1)

- Ch1 README "Up next" paragraph — reword to reflect the actual Ch2 order (fat tails first, then clustering). Current text frames clustering as the headline; new text should preview both, in the order Ch2 covers them.
- Top-level `README.md` curriculum table — Ch2 row gets its title swapped from *"coming next"* to *"Risk: Volatility Clustering and Fat Tails"* once the chapter ships.

## 12. Open questions

None at design-approval time. Implementation may surface small choices (e.g., exact rolling-window length for the comparison plot, whether to use `scipy.stats.probplot` directly or compute Q-Q manually for clarity) — those are routine implementation calls and don't need spec-level resolution.
