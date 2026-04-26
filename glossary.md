# Glossary

A running, alphabetical reference for every domain term used in this guide.
Each entry notes the chapter where the term is first introduced; consult that
chapter's prose for the term in context.

If you hit a term anywhere in the guide that isn't defined here, that's a bug
— please flag it.

---

## A

**Adjusted close** *(Ch. 1)* — The closing price of a security, retroactively
corrected for *splits* and *dividends* so that the percentage change between
any two adjusted closes equals the actual return earned by a holder. Always
use adjusted close for return calculations.

**Annualizing** *(Ch. 1)* — Rescaling a per-period statistic (typically daily)
to a yearly basis. For mean returns, multiply by ~252 trading days; for
volatility, multiply by √252 (see *√t rule*).

**Autocorrelation (*ρ<sub>k</sub>*)** *(Ch. 2)* — The correlation of a series
with a lagged copy of itself: *ρ<sub>k</sub>* = Cov(*X<sub>t</sub>*,
*X<sub>t−k</sub>*) / Var(*X<sub>t</sub>*). Near zero for daily returns, but
clearly positive for |returns| — the formal fingerprint of volatility
clustering.

## B

**Bear market** *(Ch. 1)* — A sustained market decline of roughly 20% or more
from a recent peak. The threshold is a convention, not a law.

**Bull market** *(Ch. 1)* — A sustained rally of roughly 20% or more from a
recent trough. Mirrors *bear market*.

## C

**Compounding** *(Ch. 1)* — The fact that multi-period simple returns
*multiply* rather than add: a 5-day return is `(1 + r₁)(1 + r₂)…(1 + r₅) − 1`.
This is why log returns are convenient — they add.

**Correction** *(Ch. 1)* — A market decline of roughly 10–20% from a recent
peak. Steeper sustained declines are called *bear markets*.

**Covariance** *(Ch. 2)* — Cov(*X*, *Y*) = E[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)]. The average product of two variables' deviations from
their means. Positive when *X* and *Y* tend to be above/below their means
together, negative when they move oppositely, zero when independent. Variance
is the special case Cov(*X*, *X*). The numerator of correlation and
autocorrelation. Will reappear as the central object of Chapter 3 (correlation
between assets).

## D

**Distribution** *(Ch. 1)* — The shape describing how often each value occurs
in a dataset. For a return series, the distribution answers "what fraction of
days had a return near each level."

**Dividend** *(Ch. 1)* — A cash payment from a company to its shareholders.
Adjusted close prices fold dividends back into historical prices so that
returns reflect total holder earnings.

**Drawdown** *(Ch. 1)* — The peak-to-trough decline in price over some window,
usually expressed as a percent. *Max drawdown* — the worst such decline — is
a standard risk metric.

## E

**Equity** *(Ch. 1)* — An ownership share in a company; in everyday language,
"stock."

**ETF (Exchange-Traded Fund)** *(Ch. 1)* — A pooled investment vehicle that
holds a basket of assets and itself trades on an exchange like a single stock.
Index ETFs (e.g., SPY) are designed to track a specific *index*.

**Expected value (*E*[·])** *(Ch. 2)* — The average of the bracketed quantity
over the data. For a sample of *n* observations, *E*[*x*] = (*x*<sub>1</sub> +
… + *x<sub>n</sub>*) / *n* — the same operation as the *mean*. The bracket
notation lets us cleanly write averages of more complex expressions, like
*E*[(*X* − *μ*)²] for variance or *E*[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)] for covariance.

**Excess kurtosis** *(Ch. 2)* — Kurtosis minus 3, so the normal-distribution
benchmark equals zero. Positive values mean tails heavier than the normal
predicts.

**EVT (extreme value theory)** *(Ch. 2)* — A family of statistical models for
the tails of a distribution, used when the normal-distribution model
underestimates the frequency of extreme events. Mentioned in Ch. 2 as a
deferred topic.

## F

**Fat tails** *(Ch. 1)* — A distribution whose tails carry more probability
mass than a *normal distribution* would predict — i.e., extreme moves happen
more often than a Gaussian model says they should. An empirical feature of
real return distributions.

**First moment** *(Ch. 2)* — The mean of a distribution. Daily returns are
approximately first-moment-stationary.

## G

**GARCH** *(Ch. 2)* — Generalized AutoRegressive Conditional
Heteroskedasticity. A family of time-series models that explicitly captures
volatility clustering by making the conditional variance depend on recent
shocks. Mentioned in Ch. 2 as a deferred topic.

## H

**Histogram** *(Ch. 1)* — A bar chart that buckets observations into ranges
(*bins*) and draws a bar whose height shows how many observations fall in
each bin. The visual representation of an empirical distribution.

## I

**i.i.d. (independent and identically distributed)** *(Ch. 1)* — An assumption
that each observation in a series is drawn from the *same* probability
distribution, and isn't influenced by any of the others. Real-world returns
are only approximately i.i.d.; many quant results are derived under the
assumption and need to be checked for robustness when it fails.

**Index** *(Ch. 1)* — A rule-based basket of securities meant to represent a
market or market segment (e.g., the S&P 500 represents large-cap U.S.
equities). Indexes are abstract numbers; you usually invest in them via *ETFs*
or index funds.

## K

**Kurtosis (*K*)** *(Ch. 2)* — *K* = E[(*r* − *μ*)⁴] / *σ*⁴. A measure of how
heavy a distribution's tails are. Equals 3 for a normal distribution; report
*K* − 3 (excess kurtosis) so the normal benchmark is zero.

## L

**Lag (*k*)** *(Ch. 2)* — The number of periods by which a series is shifted
when computing autocorrelation.

**Leptokurtic** *(Ch. 2)* — Technical adjective for "fat-tailed": having
excess kurtosis greater than zero.

**Log return** *(Ch. 1)* — The natural logarithm of the price ratio between
two periods: `ln(Pₜ / Pₜ₋₁)`. Log returns *add* across periods, which makes
multi-period math simpler.

## M

**Mean (μ)** *(Ch. 1)* — The arithmetic average. Sum the values, divide by
the count.

## N

**Natural logarithm (`ln`)** *(Ch. 1)* — Logarithm base *e* (≈ 2.71828).
The inverse of `eˣ`.

**Normal distribution** *(Ch. 1)* — Also called the *Gaussian* or *bell
curve*. A symmetric, single-peaked distribution fully described by its mean
and standard deviation. A common modeling default for returns; useful but
known to underestimate the frequency of extreme moves.

## O

**OHLCV** *(Ch. 1)* — Standard set of daily price columns: **O**pen,
**H**igh, **L**ow, **C**lose, **V**olume.

## P

**Price series** *(Ch. 1)* — A sequence of an asset's prices indexed by time
(typically one observation per trading day for daily data). The starting
primitive of nearly every quant analysis.

## Q

**Q-Q plot** *(Ch. 2)* — Quantile–quantile plot. A visual diagnostic that
plots the empirical quantiles of a dataset against the theoretical quantiles
of a reference distribution (often the normal). Points lie on a 45° line if
the data matches the reference; tails bending away signal fat tails.

**Quantile** *(Ch. 2)* — A cut-point along a distribution. The *p*-th quantile
is the value below which a fraction *p* of the data falls. The 0.5 quantile
is the **median**; the 0.25 and 0.75 quantiles are the first and third
**quartiles**. A distribution is fully described by the list of all its
quantiles.

**Quantitative ("quant") analysis** *(Ch. 1)* — The practice of using data
and mathematics to make decisions about financial markets, in contrast to
qualitative judgment about a company's prospects.

## R

**Regime** *(Ch. 2)* — A persistent macro-state of the market with
characteristic statistical properties (typical vol level, trend direction).
Volatility clustering is a manifestation of regime persistence.

**Return** *(Ch. 1)* — Percentage change in price between two times.
**Simple return** = `Pₜ / Pₜ₋₁ − 1`. **Log return** = `ln(Pₜ / Pₜ₋₁)`. Returns
are unitless and roughly comparable across assets, which is why we work in
returns rather than prices.

**Risk** *(Ch. 1)* — In quantitative finance, the *uncertainty* of an asset's
future return — not specifically "the chance of loss." Most often quantified
as *volatility* (std dev of returns), though Chapter 2 introduces other
measures.

**Rolling window** *(Ch. 2)* — A sliding subset of a time series used to
compute a statistic at each point in time. A rolling-window standard deviation
visualizes how volatility changes through time.

## S

**S&P 500** *(Ch. 1)* — Index of the 500 largest U.S. public companies,
weighted by market capitalization. The most-watched gauge of the U.S. stock
market.

**Second moment** *(Ch. 2)* — The variance of a distribution. Daily returns
are *not* second-moment-stationary — the rolling-vol plot is the proof.

**Simple return** *(Ch. 1)* — `Pₜ / Pₜ₋₁ − 1`. The return number a brokerage
statement reports.

**Split** *(Ch. 1)* — A re-denomination of a company's shares (e.g., 2-for-1:
each existing share becomes two shares of half the price). No economic value
changes; *adjusted close* corrects historical prices for splits.

**Standard deviation (σ)** *(Ch. 1)* — Square root of the *variance*. Same
units as the underlying data, which is why it's typically the dispersion
measure we report.

**Stationarity** *(Ch. 2)* — A property of a time series whose statistical
properties (mean, variance, autocorrelation) don't change over time. Real
return series are at best approximately mean-stationary and clearly *not*
variance-stationary.

## T

**Tails** *(Ch. 1)* — The far-left and far-right ends of a distribution,
where rare extreme values live. See also *fat tails*.

**Ticker** *(Ch. 1)* — Short alphabetic symbol identifying a security on an
exchange (e.g., `SPY`, `AAPL`, `BRK-B`).

**Trading day** *(Ch. 1)* — A day on which the market in question is open.
For U.S. equities, there are roughly **252** per year (365 minus weekends and
~9 holidays).

## V

**Variance (σ²)** *(Ch. 1)* — The mean squared deviation from the mean. A
measure of dispersion; squared so that above- and below-mean deviations both
contribute positively.

**Volatility** *(Ch. 1)* — The standard deviation of returns. The standard
quant measure of risk; usually quoted *annualized* (e.g., "20% vol").

**Volatility clustering** *(Ch. 2)* — Empirical finding that periods of high
volatility follow periods of high volatility, and similarly for low. The
characteristic pattern that GARCH models attempt to capture formally.

**Volume** *(Ch. 1)* — Number of shares (or contracts) traded in a period.
A liquidity indicator; large moves on light volume are read differently than
large moves on heavy volume.

## Z

**z-score** *(Ch. 2)* — *z<sub>t</sub>* = (*r<sub>t</sub>* − *μ*) / *σ*. A
return expressed in units of standard deviations from the mean. Used in
Ch. 2's tail-count table to compare observed extreme days with the
normal-distribution prediction.

## Symbols

**√t rule** *(Ch. 1)* — Under i.i.d. assumptions, the variance of a *t*-period
sum scales linearly in *t*, so the *standard deviation* scales by `√t`. This
is why annualized volatility uses `× √252` rather than `× 252`.
