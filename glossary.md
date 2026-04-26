# Glossary

A running, alphabetical reference for every domain term used in this guide.
Each entry notes the chapter where the term is first introduced; consult that
chapter's prose for the term in context.

If you hit a term anywhere in the guide that isn't defined here, that's a bug
— please flag it.

---

## Numerals

**60/40 portfolio** *(Ch. 3)* — Canonical balanced allocation of 60% equities
(typically broad US equity) and 40% bonds (typically intermediate-to-long
Treasuries). The default "diversified" portfolio in retail and pension
contexts; works because the SPY/TLT correlation is typically negative.

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

**Conditional correlation** *(Ch. 3)* — Correlation computed on a subset of
observations, often a tail (e.g., worst-5%-of-SPY-days). Reveals how
correlations *change* in stress regimes — though Pearson conditional
correlation suffers from a truncation artifact when conditioning on extreme
values, so the heatmap-diptych approach (§4.3) is often preferred.

**Correction** *(Ch. 1)* — A market decline of roughly 10–20% from a recent
peak. Steeper sustained declines are called *bear markets*.

**Correlation matrix** *(Ch. 3)* — *N* × *N* symmetric matrix of pairwise
Pearson correlations among *N* assets. Diagonal is 1.0; off-diagonals are in
[−1, +1].

**Covariance** *(Ch. 2)* — Cov(*X*, *Y*) = E[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)]. The average product of two variables' deviations from
their means. Positive when *X* and *Y* tend to be above/below their means
together, negative when they move oppositely, zero when independent. Variance
is the special case Cov(*X*, *X*). The numerator of correlation and
autocorrelation; the central object of the *covariance matrix* in Ch. 3.

**Covariance matrix (Σ)** *(Ch. 3)* — *N* × *N* symmetric matrix where
Σ<sub>ij</sub> = Cov(*r<sub>i</sub>*, *r<sub>j</sub>*). Diagonal is variances;
off-diagonals are pairwise covariances. The natural N-asset generalization of
σ from Ch. 2; the input to portfolio-variance calculations.

**Crisis correlation** *(Ch. 3)* — Informal name for the empirical finding
that the *structure* of correlations changes during stress regimes —
typically with most off-diagonal entries climbing toward 1, weakening
diversification when it's needed most.

## D

**Distribution** *(Ch. 1)* — The shape describing how often each value occurs
in a dataset. For a return series, the distribution answers "what fraction of
days had a return near each level."

**Diversification benefit** *(Ch. 3)* — The reduction in a portfolio's
volatility below the weighted average of its individual assets' volatilities,
attributable to *ρ* < 1 (and amplified when *ρ* < 0).

**Diversification floor** *(Ch. 3)* — When all pairwise correlations equal a
common value *ρ*, the equal-weighted portfolio variance ratio
*σ<sub>p</sub>²* / *σ²* approaches *ρ* as *N* → ∞ — the irreducible
(systematic) portion of risk that no amount of diversification can remove.

**Dividend** *(Ch. 1)* — A cash payment from a company to its shareholders.
Adjusted close prices fold dividends back into historical prices so that
returns reflect total holder earnings.

**Drawdown** *(Ch. 1)* — The peak-to-trough decline in price over some window,
usually expressed as a percent. *Max drawdown* — the worst such decline — is
a standard risk metric.

## E

**Equal-weight portfolio** *(Ch. 3)* — A portfolio in which every asset has
the same weight 1/*N*. The simplest non-trivial weighting scheme; useful as
a benchmark, but tends to over-allocate to high-volatility assets compared
with risk-aware schemes.

**Equity** *(Ch. 1)* — An ownership share in a company; in everyday language,
"stock."

**ETF (Exchange-Traded Fund)** *(Ch. 1)* — A pooled investment vehicle that
holds a basket of assets and itself trades on an exchange like a single stock.
Index ETFs (e.g., SPY) are designed to track a specific *index*.

**EVT (extreme value theory)** *(Ch. 2)* — A family of statistical models for
the tails of a distribution, used when the normal-distribution model
underestimates the frequency of extreme events. Mentioned in Ch. 2 as a
deferred topic.

**Excess kurtosis** *(Ch. 2)* — Kurtosis minus 3, so the normal-distribution
benchmark equals zero. Positive values mean tails heavier than the normal
predicts.

**Expected value (*E*[·])** *(Ch. 2)* — The average of the bracketed quantity
over the data. For a sample of *n* observations, *E*[*x*] = (*x*<sub>1</sub> +
… + *x<sub>n</sub>*) / *n* — the same operation as the *mean*. The bracket
notation lets us cleanly write averages of more complex expressions, like
*E*[(*X* − *μ*)²] for variance or *E*[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)] for covariance.

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
shocks. Mentioned in Ch. 2 as a deferred topic. (Ch. 3's analogue for
correlations is **DCC-GARCH**, also deferred.)

## H

**Hidden factor exposure** *(Ch. 3)* — The phenomenon that seemingly distinct
assets share underlying drivers (interest rates, oil, the broad market
itself), so a "diversified" portfolio may be a single bet. Named in Ch. 3 as
a deferred flavor of correlation risk; formal treatment in a future
factor-models chapter.

**Histogram** *(Ch. 1)* — A bar chart that buckets observations into ranges
(*bins*) and draws a bar whose height shows how many observations fall in
each bin. The visual representation of an empirical distribution.

## I

**Idiosyncratic risk** *(Ch. 3)* — The asset-specific portion of risk that
can be diversified away in a sufficiently large basket. Complement of
*systematic risk*. Decomposition of risk into idiosyncratic + systematic is
the seed of CAPM and factor models.

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

**Pearson correlation (*ρ*)** *(Ch. 3)* — *ρ<sub>XY</sub>* = Cov(*X*, *Y*) /
(*σ<sub>X</sub> σ<sub>Y</sub>*). The unitless, scale-free version of
covariance; bounded in [−1, +1]; the building block of every portfolio-risk
calculation.

**Portfolio variance / standard deviation (σ<sub>p</sub>)** *(Ch. 3)* —
Variance / standard deviation of a weighted basket's return. Computable from
individual volatilities and pairwise correlations via *σ<sub>p</sub>²* =
**w**ᵀ **Σ** **w**.

**Portfolio weights (w)** *(Ch. 3)* — Vector of allocations across assets;
sums to 1 for a fully-invested long-only portfolio.

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
Volatility clustering is a manifestation of regime persistence; correlation
structure also shifts across regimes (Ch. 3).

**Return** *(Ch. 1)* — Percentage change in price between two times.
**Simple return** = `Pₜ / Pₜ₋₁ − 1`. **Log return** = `ln(Pₜ / Pₜ₋₁)`. Returns
are unitless and roughly comparable across assets, which is why we work in
returns rather than prices.

**Risk** *(Ch. 1)* — In quantitative finance, the *uncertainty* of an asset's
future return — not specifically "the chance of loss." Most often quantified
as *volatility* (std dev of returns); Ch. 2's "What we mean by risk" framing
breaks risk into magnitude / persistence / path / correlation flavors.

**Rolling correlation** *(Ch. 3)* — Pairwise correlation computed over a
sliding window of recent observations. Reveals time-variation that a
single-number long-run correlation hides — e.g., the SPY/TLT correlation
flipping signs across regimes.

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

**Systematic risk** *(Ch. 3)* — The portion of risk that *can't* be
diversified away — common factor exposure shared across many assets.
Complement of *idiosyncratic risk*; formalized via factor models in later
chapters.

## T

**Tail dependence** *(Ch. 3)* — When two assets correlate primarily (or only)
in the extreme tails of the joint distribution. Standard linear correlation
can't capture this. Named in Ch. 3 as a deferred flavor of correlation risk;
treatment alongside EVT and copulas much later.

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

**√N rule** *(Ch. 3)* — *σ<sub>p</sub>* = *σ* / √*N* for an equal-weighted
portfolio of *N* uncorrelated assets with common volatility *σ*. The most
diversification mathematically possible; a useful upper-bound benchmark.

**√t rule** *(Ch. 1)* — Under i.i.d. assumptions, the variance of a *t*-period
sum scales linearly in *t*, so the *standard deviation* scales by `√t`. This
is why annualized volatility uses `× √252` rather than `× 252`.
