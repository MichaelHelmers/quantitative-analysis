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

**`arch` package** *(Ch. 9, named only)* — Kevin Sheppard's Python library for GARCH-family models. *Currently broken under pandas 3.0* (the unmaintained `deprecate_kwarg` API change), so Ch. 9 implements GARCH(1,1) and DCC by hand via `scipy.optimize` instead — which is pedagogically cleaner since the chapter's MLE primer is the headline learning.

**ARCH** *(Ch. 9, named only)* — Autoregressive Conditional Heteroskedasticity. The simpler precursor to GARCH (no GARCH lag, just ARCH lags). Engle (1982). GARCH absorbed it as a special case.

**Annualized Sharpe** *(Ch. 5)* — A Sharpe ratio expressed on a yearly basis. For daily-return Sharpe, multiply by **√252** (not 252) — the numerator scales by 252 and the denominator by √252, so the ratio scales by 252 / √252 = √252.

**Adjusted R²** *(Ch. 7)* — R² penalised for added regressors: *R²<sub>adj</sub>* = 1 − (1 − R²) · (n − 1) / (n − k − 1), where *k* is the number of regressors. For simple regression *R²<sub>adj</sub>* ≈ R²; matters in multiple regression.

**Autocorrelated residuals** *(Ch. 7)* — Regression residuals where *ε̂<sub>t</sub>* predicts *ε̂<sub>t+1</sub>*. Breaks the i.i.d. SE assumption underlying textbook OLS standard errors. Diagnosed via residual ACF; partly fixed by HAC SEs (`cov_type='HAC'`); fully fixed by GARCH for the variance (Ch. 9).

**Autocorrelation (*ρ<sub>k</sub>*)** *(Ch. 2)* — The correlation of a series
with a lagged copy of itself: *ρ<sub>k</sub>* = Cov(*X<sub>t</sub>*,
*X<sub>t−k</sub>*) / Var(*X<sub>t</sub>*). Near zero for daily returns, but
clearly positive for |returns| — the formal fingerprint of volatility
clustering.

## B

**β (beta)** *(Ch. 8; named Ch. 3)* — Slope on a factor in a regression — most commonly the slope on the market in a CAPM regression. The single most-cited number in equity finance: β = 1 means an asset moves 1-for-1 with the market on average; β > 1 amplifies systematic moves; β < 1 dampens them.

**Bear market** *(Ch. 1)* — A sustained market decline of roughly 20% or more
from a recent peak. The threshold is a convention, not a law.

**Bias** *(Ch. 4)* — The expected difference between an estimator's value and
the true population value it's trying to estimate. An *unbiased* estimator
has bias = 0. The sample mean is unbiased for the population mean.

**Black-Litterman** *(Ch. 6, named only)* — Bayesian framework that combines an equilibrium prior on expected returns with an investor's subjective views to produce a stable posterior used as MVO input. The standard institutional response to mean-variance instability when *r<sub>f</sub>*-based shrinkage isn't enough.

**Block bootstrap** *(Ch. 6)* — Bootstrap resampling that draws *blocks* of consecutive observations rather than single points, preserving short-horizon dependence (volatility clustering, autocorrelation). Block length is a hyperparameter; 21 days is a common default for daily financial data.

**Block maxima (BM)** *(Ch. 10 §2, named only)* — EVT flavor: divide data into non-overlapping blocks (e.g., calendar years), take the maximum in each, fit a GEV distribution to the resulting maxima. Pedagogically clean but wasteful — uses ~20 of 5,000 observations on annual blocks. **Peaks-over-threshold (POT) is the daily-return choice** instead.

**Bias–variance tradeoff** *(Ch. 4)* — The principle that accepting a small
bias in an estimator can sometimes reduce its overall mean-squared error.
Underlies shrinkage estimators and a huge swath of statistics and ML.

**Bull market** *(Ch. 1)* — A sustained rally of roughly 20% or more from a
recent trough. Mirrors *bear market*.

## C

**CAPM (Capital Asset Pricing Model)** *(Ch. 8)* — Single-factor regression model: R<sub>i,t</sub> − r<sub>f,t</sub> = α + β·(R<sub>mkt,t</sub> − r<sub>f,t</sub>) + ε<sub>i,t</sub>. The simplest factor model in finance; β captures market exposure and α captures the residual mean. Operationally a one-regressor OLS fit; the textbook normative derivation (utility, market clearing) is out of scope here.

**Capital Market Line (CML)** *(Ch. 6)* — In (σ, μ) space, the straight line through the risk-free point (0, *r<sub>f</sub>*) and the **tangency portfolio**. Every Sharpe-maximizing investor's holdings sit on this line — risk-averse investors blend in *r<sub>f</sub>*, risk-tolerant investors lever the tangency portfolio. The geometric realization of the **two-fund separation theorem**.

**Calmar ratio** *(Ch. 5, named only)* — A risk-adjusted-return ratio that uses absolute max drawdown in the denominator instead of vol. Penalizes path risk directly; complementary to Sharpe rather than a replacement.

**Clayton copula** *(Ch. 10 §6)* — Asymmetric copula; non-zero lower-tail dependence, zero upper-tail dependence. Sometimes used for credit defaults where joint downside crashes are the concern.

**CMA (Conservative Minus Aggressive)** *(Ch. 8 §7)* — Investment factor in Fama-French 5-factor model. Daily return of a portfolio long firms with low investment growth, short high. Marginal R² gain over FF3 on diversified ETFs is small.

**Compounding** *(Ch. 1)* — The fact that multi-period simple returns
*multiply* rather than add: a 5-day return is `(1 + r₁)(1 + r₂)…(1 + r₅) − 1`.
This is why log returns are convenient — they add.

**Conditional correlation** *(Ch. 3)* — Correlation computed on a subset of
observations, often a tail (e.g., worst-5%-of-SPY-days). Reveals how
correlations *change* in stress regimes — though Pearson conditional
correlation suffers from a truncation artifact when conditioning on extreme
values, so the heatmap-diptych approach (§4.3) is often preferred.

**Conditional VaR (CVaR)** *(Ch. 5)* — Expected loss *given* that the loss exceeds the VaR threshold: *CVaR<sub>α</sub>* = − E[*r* | *r* ≤ *Q<sub>α</sub>*(*r*)]. Synonym: **Expected Shortfall (ES)**. Always ≥ VaR by construction. Captures the *shape* of the tail past the threshold; VaR alone doesn't.

**Copula** *(Ch. 10 §6)* — Joint distribution of two or more random variables after transforming each marginal to Uniform[0, 1]. Strips out marginal shape; what remains is *pure dependence*. Sklar's theorem says any joint distribution = marginals + a copula. Lets you model the marginals (e.g., GPD for tails) separately from the dependence.

**Conditional vs unconditional vol** *(Ch. 9)* — *Conditional* = today's σ given history; *unconditional* = whole-sample average σ. GARCH provides the conditional version; the constant-σ assumption used in Ch. 5 VaR is the unconditional version.

**Confidence interval** *(Ch. 4; generalized Ch. 7 §3)* — A range around a point estimate that
contains the true population value with stated probability under repeated
sampling. *μ̂* ± 1.96 · SE gives a 95% CI under approximate normality of
the sample mean. In OLS regression, the same form gives a CI on each
coefficient: *β̂* ± 1.96 · SE(*β̂*).

**Confidence level (α)** *(Ch. 5)* — In VaR / CVaR usage, the tail probability the metric refers to. "5% VaR" means the worst-5% threshold. Smaller α means deeper into the tail. Distinct from the *confidence level* in a CI — opposite sign convention (95% CI ↔ α = 0.05).

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

**Cross-sectional mean** *(Ch. 4)* — The mean across assets at a single
point in time, in contrast to a time-series mean (one asset across many
points). The default prior in James-Stein shrinkage applied to a basket.

## D

**Delta method** *(Ch. 5)* — First-order Taylor approximation used to derive the standard error of a function of estimators (e.g., Sharpe = *μ̂* / *σ̂*) from the SEs of the inputs. The Ch. 5 §4.3 derivation gives *SE(Sharpe)* ≈ √((1 + Sharpe²/2) / N) under normality.

**DCC-GARCH** *(Ch. 9 §6)* — Dynamic Conditional Correlation; multivariate GARCH for time-varying correlations. Two steps: (1) per-asset GARCH on each series; (2) update the correlation matrix as a GARCH-style recursion on standardised residuals. Two extra parameters (a, b) MLE-fit on top of per-asset GARCHs. Captures Ch3's regime-shift correlations (e.g., SPY/TLT 2022 sign flip) more cleanly than rolling-window correlation.

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

**Drawdown** *(Ch. 1, formalized Ch. 5)* — How far below the running peak the price currently sits: *DD*(*t*) = (*P*(*t*) − *P*<sub>peak</sub>(*t*)) / *P*<sub>peak</sub>(*t*). Always ≤ 0 in our negative-decimal convention. **Max drawdown (MDD)** — the most negative *DD*(*t*) over a window — is the headline path-risk metric (Ch. 5 §2).

## E

**Efficient frontier** *(Ch. 6)* — The set of portfolios offering the lowest variance for each achievable return target — equivalently, the upper branch of the (σ, μ) curve traced by the mean-variance program. Every individual asset sits *inside* the frontier (diversification dominance); the leftmost point is the **GMV**; the *tangency point* (where the **CML** kisses the curve) is the maximum-Sharpe portfolio.

**Equal Risk Contribution (ERC)** *(Ch. 6)* — Synonym for **risk parity**. The portfolio chosen so that every asset's *RC*<sub>i</sub> = *σ*<sub>p</sub>/*K*. No closed form; solved numerically.

**Equal-weight portfolio** *(Ch. 3)* — A portfolio in which every asset has
the same weight 1/*N*. The simplest non-trivial weighting scheme; useful as
a benchmark, but tends to over-allocate *risk* to high-volatility assets compared with risk-aware schemes — see **risk contribution** for the audit.

**Estimation error / instability** *(Ch. 6)* — The effect of input noise (μ̂, Σ̂) on optimization output (weights). Mean-variance amplifies it through Σ⁻¹: small differences in expected returns get levered into very different "optimal" weights. Demonstrated by bootstrap resamples whose tangency XLK weight ranges from 0% to 100% on the same 20-year data.

**Equilibrium / required return** *(Ch. 4)* — The expected return an asset
*should* have given its risk and factor exposures. Named in Ch. 4 as a
deferred flavor; formalized in Ch. 8 (CAPM, Fama-French).

**Equity** *(Ch. 1)* — An ownership share in a company; in everyday language,
"stock."

**Estimator** *(Ch. 4)* — A function of data used to guess an unknown
population quantity. The sample mean is an estimator of the population mean;
the sample variance is an estimator of the population variance.

**ETF (Exchange-Traded Fund)** *(Ch. 1)* — A pooled investment vehicle that
holds a basket of assets and itself trades on an exchange like a single stock.
Index ETFs (e.g., SPY) are designed to track a specific *index*.

**EWMA (Exponentially-Weighted Moving Average)** *(Ch. 9)* — Closed-form vol recursion: σ²<sub>t</sub> = (1−λ) ε²<sub>t-1</sub> + λ σ²<sub>t-1</sub>. Single hyperparameter λ; no fitting. RiskMetrics defaults: λ = 0.94 (daily), 0.97 (monthly). **Cheap and intuitive but has no long-run vol** — drifts forever after a regime change. GARCH fixes this.

**EGARCH** *(Ch. 9, named only)* — Asymmetric GARCH variant capturing the leverage effect (negative shocks raise vol more than positive shocks of equal magnitude). Out of scope; GARCH(1,1) is the curriculum's baseline.

**EVT (extreme value theory)** *(Ch. 2; formalized Ch. 10)* — A family of statistical models for
the tails of a distribution, used when the normal-distribution model
underestimates the frequency of extreme events. Two main flavors: **block maxima** (fit GEV to per-block maxima) and **peaks-over-threshold (POT)** (fit GPD to exceedances above a chosen threshold). Ch. 10 uses POT — more efficient on daily-return data.

**EVT-VaR / EVT-ES** *(Ch. 10 §4)* — VaR / ES computed from the GPD parametric form. Closed form: VaR<sub>q</sub> = u + (σ̂/ξ̂) · [((n/n<sub>u</sub>)·q)<sup>−ξ̂</sup> − 1]. **Extrapolates beyond the sample**, which Historical can't and Gaussian gets wrong. Bootstrap CI is wide (~30%+ of point estimate at q=0.001) — extrapolation gives you a number, not certainty.

**Excess kurtosis** *(Ch. 2)* — Kurtosis minus 3, so the normal-distribution
benchmark equals zero. Positive values mean tails heavier than the normal
predicts.

**Excess return** *(Ch. 5)* — Asset return minus the risk-free rate: *r*<sub>excess,t</sub> = *r<sub>t</sub>* − *r*<sub>f,t</sub>. The compensation for taking risk; the input to Sharpe-style metrics. Earning the risk-free rate isn't compensation for risk — you could have it without taking any.

**Expected Shortfall (ES)** *(Ch. 5)* — Synonym for **Conditional VaR (CVaR)**.

**Expected value (*E*[·])** *(Ch. 2)* — The average of the bracketed quantity
over the data. For a sample of *n* observations, *E*[*x*] = (*x*<sub>1</sub> +
… + *x<sub>n</sub>*) / *n* — the same operation as the *mean*. The bracket
notation lets us cleanly write averages of more complex expressions, like
*E*[(*X* − *μ*)²] for variance or *E*[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)] for covariance.

## F

**Factor** *(Ch. 8)* — A common driver of asset returns. Examples: the market itself (CAPM), size and value (Fama-French 3), profitability and investment (Fama-French 5). Factor models decompose any asset's return into β-weighted factor exposures plus α plus an idiosyncratic residual.

**Factor exposure / loading** *(Ch. 8)* — The β coefficient on a factor in a regression. "Loading" and "exposure" are interchangeable; both mean "how much of this factor does this asset carry?"

**Factor zoo** *(Ch. 8 §8, named only)* — The proliferation of published factors since Fama and French (1992) — hundreds in the literature. Most don't survive replication or out-of-sample tests. The empirical-finance toolkit is much smaller than the publication record suggests.

**Fama-French 3-factor model (FF3)** *(Ch. 8)* — Multi-regressor factor model: market + SMB + HML. The canonical workhorse of academic empirical asset pricing. R² typically 5-10pp higher than CAPM on diversified equity portfolios.

**Fama-French 5-factor model (FF5)** *(Ch. 8)* — FF3 + RMW + CMA (profitability + investment). Marginal R² gain over FF3 is small on diversified ETFs; matters more on individual stocks.

**Fat tails** *(Ch. 1)* — A distribution whose tails carry more probability
mass than a *normal distribution* would predict — i.e., extreme moves happen
more often than a Gaussian model says they should. An empirical feature of
real return distributions.

**First moment** *(Ch. 2)* — The mean of a distribution. Daily returns are
approximately first-moment-stationary.

**Filtered historical simulation (FHS)** *(Ch. 10 §3.4; named in Ch. 9 §5)* — Production-grade tail-VaR construction: standardise returns by GARCH σ̂<sub>t</sub>, fit EVT-GPD on the standardised residuals, recombine today's σ̂<sub>T</sub> with the residual tail-shape. **GARCH for the variance, EVT for the tail shape.** ξ̂ on standardised residuals (≈0.06 for SPY) is much smaller than ξ̂ on raw returns (≈0.19) — GARCH absorbs most of the fat-tail behavior.

**Fitted value** *(Ch. 7)* — The model's prediction at an observed *x*: *ŷ<sub>t</sub>* = *α̂* + *β̂*·*x<sub>t</sub>*. The y-coordinate of the regression line at *x<sub>t</sub>*. The *residual* is observed minus fitted.

**Forecast / conditional expected return** *(Ch. 4)* — Expected return *given
current state* — a prediction that varies day-to-day, in contrast to the
long-run unconditional mean. Named in Ch. 4 as a deferred flavor; formalized
in Ch. 8 and Ch. 11–12.

## G

**Gaussian copula** *(Ch. 10 §6)* — Copula induced by the multivariate normal distribution. **λ<sub>U</sub> = λ<sub>L</sub> = 0 *regardless of correlation*** — has *no* tail dependence even when ρ < 1. The implicit assumption behind the 2008 CDO model failures: subprime defaults priced under a Gaussian-copula assumption could not, mathematically, see joint extreme defaults coming.

**GEV (Generalized Extreme Value)** *(Ch. 10 §2, named only)* — The limit distribution for block maxima in EVT. Used with the block-maxima approach; out-of-scope for this curriculum (POT-GPD is the daily-return choice).

**GPD (Generalized Pareto Distribution)** *(Ch. 10 §2)* — Two-parameter (ξ, σ) distribution that, by the Pickands-Balkema-de Haan theorem, is the limit distribution for exceedances above a high threshold. Density: f(y; ξ, σ) = (1/σ)·(1 + ξ·y/σ)<sup>−1/ξ−1</sup>. Three regimes via ξ: heavy (ξ > 0), exponential (ξ = 0), bounded (ξ < 0). Daily equity tails sit at ξ ≈ 0.15-0.25.

**GARCH(1,1)** *(Ch. 9; named Ch. 2)* — σ²<sub>t</sub> = ω + α·ε²<sub>t-1</sub> + β·σ²<sub>t-1</sub>. The standard daily-equity vol model: three parameters, MLE-fit, mean-reverting to long-run σ̄ = √(ω/(1−α−β)). Persistence α + β ≈ 0.97-0.99 for daily equities — high but stable.

**GARCH-VaR** *(Ch. 9 §5)* — Ch. 5's parametric Gaussian VaR formula with σ̂<sub>t</sub> from GARCH instead of constant σ̂: VaR<sub>t</sub>(q) = z<sub>q</sub> · σ̂<sub>t</sub>. Closer to the nominal breach rate at the headline 5% horizon than constant-σ VaR; still under-prices the deepest tail (conditional Gaussian assumption — Ch. 10's EVT fixes this).

**GJR-GARCH** *(Ch. 9, named only)* — Another asymmetric GARCH variant; like EGARCH, captures leverage effect.

**Global Minimum Variance (GMV) portfolio** *(Ch. 6)* — The lowest-variance portfolio achievable from a given Σ — the leftmost point on the **efficient frontier**. Closed-form unconstrained solution: **w**<sub>GMV</sub> = **Σ**⁻¹**1** / (**1**ᵀ**Σ**⁻¹**1**). Depends only on Σ, not μ. Concentrates in low-vol, well-diversifying assets (e.g., TLT, XLV, GLD on the curriculum's 8-ticker basket).

**GARCH** *(Ch. 2; formalized Ch. 9)* — Generalized AutoRegressive Conditional
Heteroskedasticity. A family of time-series models that explicitly captures
volatility clustering by making the conditional variance depend on recent
shocks. Mentioned in Ch. 2 as a deferred topic. (Ch. 3's analogue for
correlations is **DCC-GARCH**, also deferred.)

## H

**Hidden factor exposure** *(Ch. 3; paid Ch. 8 §5)* — The phenomenon that seemingly distinct
assets share underlying drivers (interest rates, oil, the broad market
itself), so a "diversified" portfolio may be a single bet. Quantified in Ch. 8 by computing the basket's weighted-average β: EW8 over the curriculum's 8-ticker basket has β ≈ 0.69 and R² on SPY ≈ 0.90 — *the basket is essentially a one-factor object.*

**HML (High Minus Low)** *(Ch. 8)* — Value factor in Fama-French 3-factor model. Daily return of a portfolio long high-book-to-market (value) stocks and short low (growth) stocks. Positive on days value beats growth. XLF loads strongly positive (banks are value); XLK loads strongly negative (tech is growth).

**Heteroskedasticity** *(Ch. 7)* — Residual variance that depends on *x* (or on time). Breaks the textbook OLS standard-error formulas, which assume constant residual variance (*homoskedasticity*). Diagnosed via residuals-vs-fitted plot (fan shape); partly fixed by HAC SEs.

**Histogram** *(Ch. 1)* — A bar chart that buckets observations into ranges
(*bins*) and draws a bar whose height shows how many observations fall in
each bin. The visual representation of an empirical distribution.

**Historical VaR** *(Ch. 5)* — VaR computed empirically as a quantile of the observed return distribution: *VaR<sub>α</sub>* = − *Q<sub>α</sub>*(*r*). No distributional assumption. Preferred to Gaussian VaR for daily equity tails at α ≤ 1% (where the fat-tail premium materially bites).

## I

**Idiosyncratic risk** *(Ch. 3; formalized Ch. 8 §2)* — The asset-specific portion of risk that
can be diversified away in a sufficiently large basket — the residual ε in a factor-model regression. Complement of *systematic risk*.

**Intercept (*α̂*)** *(Ch. 7)* — The constant term in a linear regression: the average of *y* when *x* = 0. In CAPM-style regressions, the intercept of (asset − r<sub>f</sub>) on (market − r<sub>f</sub>) is the famous *α* — "everything not explained by market exposure" (Ch. 8).

## J

**James-Stein estimator** *(Ch. 4)* — A specific shrinkage estimator that
strictly dominates the sample mean in total MSE for *K* ≥ 3 assets shrunk
together. The positive-part version is the standard practical form. Used
widely in production portfolio optimization. Decomposition of risk into idiosyncratic + systematic is
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

**Ken French data library** *(Ch. 8)* — Dartmouth-hosted source for academic factor data (FF3, FF5, momentum, industry portfolios). Daily and monthly frequencies. Returns reported in *percent* (divide by 100 before regressing on log returns). The standard `pandas-datareader` route is broken under pandas 3.0; download CSV zips directly from the Dartmouth FTP.

**Kurtosis (*K*)** *(Ch. 2)* — *K* = E[(*r* − *μ*)⁴] / *σ*⁴. A measure of how
heavy a distribution's tails are. Equals 3 for a normal distribution; report
*K* − 3 (excess kurtosis) so the normal benchmark is zero.

## L

**Lag (*k*)** *(Ch. 2)* — The number of periods by which a series is shifted
when computing autocorrelation.

**Least squares** *(Ch. 7)* — The procedure of fitting a line (or hyperplane) by minimising the sum of squared residuals: SS(α, β) = Σ (y<sub>t</sub> − α − β·x<sub>t</sub>)². Closed-form solutions: *β̂* = Cov(x, y) / Var(x), *α̂* = ȳ − β̂·x̄.

**Long-run / unconditional vol** *(Ch. 9)* — Under GARCH(1,1), σ̄ = √(ω/(1−α−β)) is the steady-state vol the process mean-reverts to. For SPY 20y, σ̄ ≈ 18% annualized — close to the whole-sample sample σ ≈ 19.5%, sanity-checking the model.

**Log-likelihood** *(Ch. 9 §3.2)* — Sum of log-densities of observations under a parametric model. MLE picks parameters that maximise the log-likelihood. For GARCH with conditional Gaussian innovations: log L = −½ Σ [log σ²<sub>t</sub> + ε²<sub>t</sub>/σ²<sub>t</sub>].

**Look-ahead bias** *(Ch. 7)* — Using information from time *t+1* (or later) to compute a feature or target at time *t*. Inflates apparent predictive power; the regression looks better in-sample than it can ever do live. The procedural fix: every feature available at *t* must be derivable strictly before *t*. Revisited rigorously in Ch. 13.

**Ledoit-Wolf shrinkage** *(Ch. 6, named only)* — Shrinkage estimator for the covariance matrix Σ̂, the analog of Ch. 4's James-Stein shrinkage on μ̂. Pulls Σ̂ toward a structured target (typically the diagonal) by a data-driven amount. Reduces the off-diagonal noise that Σ⁻¹ otherwise amplifies.

**Long-only constraint** *(Ch. 6)* — Optimization restriction *w*<sub>i</sub> ≥ 0 — no short selling. Acts as a statistical regularizer on top of its business meaning: caps the levering effect of Σ⁻¹ on noisy μ̂, often at near-zero vol cost on diversified baskets.

**Leptokurtic** *(Ch. 2)* — Technical adjective for "fat-tailed": having
excess kurtosis greater than zero.

**Log return** *(Ch. 1)* — The natural logarithm of the price ratio between
two periods: `ln(Pₜ / Pₜ₋₁)`. Log returns *add* across periods, which makes
multi-period math simpler.

## M

**Mean (μ)** *(Ch. 1)* — The arithmetic average. Sum the values, divide by
the count.

**Marginal risk contribution (MRC)** *(Ch. 6)* — *MRC*<sub>i</sub> = (**Σ****w**)<sub>i</sub> / *σ*<sub>p</sub>. The partial derivative ∂*σ*<sub>p</sub>/∂*w*<sub>i</sub> — how much portfolio vol moves when asset *i*'s weight is nudged.

**Market portfolio** *(Ch. 8)* — Theoretically, the value-weighted basket of all risky assets. In practice proxied by SPY (loose) or by Fama-French Mkt-RF (the value-weighted CRSP US universe minus *r<sub>f</sub>*; the academic standard). Ch. 8 §2.1 shows the SPY-vs-CRSP gap is statistically distinguishable over 20 years.

**Market risk premium** *(Ch. 8)* — *E*[*R*<sub>mkt</sub> − *r*<sub>f</sub>]; the expected reward for bearing one unit of market risk. The Mkt-RF Fama-French series is the realised version.

**Mean-variance optimization (MVO)** *(Ch. 6)* — Markowitz's 1952 framework: pick portfolio weights to optimize a tradeoff between portfolio mean and variance, subject to budget and (optionally) long-only constraints. Famously *unstable* on noisy inputs — see **estimation error**.

**MLE (Maximum Likelihood Estimation)** *(Ch. 9 §3.2)* — Pick parameters that make the observed data most likely under a parametric model. The standard answer when "regress on something" doesn't apply (e.g., GARCH — there's no observed σ<sub>t</sub> to regress on). Implemented numerically via `scipy.optimize.minimize` on the negative log-likelihood. *The only inferential tool the curriculum genuinely needs to introduce in Ch. 9.*

**Max drawdown (MDD)** *(Ch. 5)* — The most negative drawdown observed over a window: *MDD* = min<sub>t</sub> *DD*(*t*). The headline path-risk metric. Pair with **recovery time** for the duration coordinate.

**Mean residual life (MRL) plot** *(Ch. 10 §3)* — Plot of mean exceedance above threshold *v* against *v*. Used to pick the GPD threshold *u*: above the right *u*, the curve is approximately linear (the GPD limit has kicked in); below, it bends. Pick *u* in the linear region.

**Multicollinearity** *(Ch. 7)* — When two regressors carry near-identical information, their individual coefficients become unstable (huge SEs) even though the joint fit is fine. The (XᵀX)⁻¹ matrix that produces β̂ has the same instability shape as Ch. 6's Σ⁻¹. Symptom: small changes in data produce large coefficient swings.

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

**Omitted-variable bias (OVB)** *(Ch. 7)* — Bias in a regression coefficient from leaving out a variable that (a) explains *y* and (b) correlates with the included regressor. The included coefficient absorbs some of the omitted variable's effect. Closed form: bias on β₁ equals β₂ · Cov(x₁, x₂)/Var(x₁) when the true model has both regressors but you fit only one.

**Ordinary least squares (OLS)** *(Ch. 7)* — The standard least-squares procedure under the textbook assumptions (linear model, i.i.d. residuals, finite variance). Implemented in `statsmodels.api.OLS(y, X).fit()`. Produces point estimates plus standard errors, t-statistics, p-values, and confidence intervals.

## P

**Parametric (Gaussian) VaR** *(Ch. 5)* — VaR computed assuming returns are normal: *VaR<sub>α</sub>* = − (*μ* + *z<sub>α</sub>* · *σ*). Approximately matches historical VaR at conventional 5% levels but underestimates badly in the deep tail (1%, 0.5% — see *tail premium*).

**Peaks over threshold (POT)** *(Ch. 10 §2)* — EVT flavor: pick a high threshold *u*, fit a GPD to the exceedances (X − u | X > u). Uses ~250 observations at u = p95 over a 5,000-obs window — the daily-return choice over block maxima. Justified by the **Pickands-Balkema-de Haan theorem**.

**Persistence (α + β)** *(Ch. 9)* — Sum of GARCH(1,1) coefficients; how slowly vol shocks decay. For daily equities ≈ 0.97-0.99 (high but stable). Determines the half-life of vol shocks; the long-run variance is σ̄² = ω/(1−α−β).

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

**Prior** *(Ch. 4)* — The target value toward which a shrinkage estimator
pulls. Common choices: the cross-sectional mean of all assets being shrunk,
or zero.

**Prediction interval** *(Ch. 7)* — Error bar on a *new individual ŷ*, computed as ŷ ± 1.96 · √(σ̂²<sub>ε</sub> + SE_line(x)²). Wider than the CI on the regression line because it includes the irreducible residual scatter on top of line-fitting uncertainty.

**p-value** *(Ch. 4; formal definition Ch. 7 §3)* — Probability of seeing |t| (or any test statistic) at least this large under the null hypothesis. p < 0.05 is the conventional reject-the-null bar; *low* in finance because we test many things — Ch. 7 Exercise 4 shows random walks clear |t| > 2 in 98% of trials.

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

**R² (coefficient of determination)** *(Ch. 7)* — In-sample fraction of variance in *y* explained by the regression: R² = 1 − SS<sub>res</sub>/SS<sub>tot</sub>. Range [0, 1] with intercept; equals corr(*x*, *y*)² in simple regression. **Not** a quality score — *in-sample only*; out-of-sample R² is typically lower and can go negative.

**Realized return** *(Ch. 4)* — What actually happened over a past window.
Distinguished in Ch. 4 from "expected return" because it's the *data* used
to estimate, not the estimate itself.

**Residual** *(Ch. 7)* — Observed minus fitted in a regression: *ε̂<sub>t</sub>* = *y<sub>t</sub>* − *ŷ<sub>t</sub>*. Three diagnostic plots audit residuals — vs fitted (linearity + homoskedasticity), Q-Q vs Normal (tail behavior), ACF (autocorrelation).

**Recovery time** *(Ch. 5)* — Days between the peak preceding a drawdown and the first new peak after. The duration coordinate of path risk; complements MDD.

**RMW (Robust Minus Weak)** *(Ch. 8 §7)* — Profitability factor in Fama-French 5-factor model. Daily return of a portfolio long high-profitability firms, short low. Marginal R² gain over FF3 on diversified ETFs is small.

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

**Risk contribution (RC)** *(Ch. 6)* — *RC*<sub>i</sub> = *w*<sub>i</sub> · *MRC*<sub>i</sub>. Asset *i*'s share of total portfolio vol; the *RC*<sub>i</sub> sum to *σ*<sub>p</sub>. Can be negative for assets that *remove* risk via negative correlation (e.g., TLT in an equity-heavy basket).

**Risk parity** *(Ch. 6)* — Portfolio chosen so that every asset's risk contribution is equal: *RC*<sub>i</sub> = *σ*<sub>p</sub>/*K* for all *i*. Synonym: **Equal Risk Contribution (ERC)**. Depends on Σ only, not μ — the standard practitioner response to mean-variance instability when μ-estimates aren't trustworthy. Generalizes the 60/40 instinct ("over-weight the low-vol asset to balance risk") to *K* assets.

**Risk-free rate (*r<sub>f</sub>*)** *(Ch. 5)* — The yield on a (effectively) zero-default-risk asset; **T-bill** yield in practice. Subtracted from asset returns to compute *excess returns*. Use the rolling daily series, not a constant — the 20y window spans 0% (ZIRP) and 5% rate regimes.

**Rolling correlation** *(Ch. 3)* — Pairwise correlation computed over a
sliding window of recent observations. Reveals time-variation that a
single-number long-run correlation hides — e.g., the SPY/TLT correlation
flipping signs across regimes.

**Rolling window** *(Ch. 2)* — A sliding subset of a time series used to
compute a statistic at each point in time. A rolling-window standard deviation
visualizes how volatility changes through time.

**Running peak** *(Ch. 5)* — The maximum of a price series up to and including time *t*: *P*<sub>peak</sub>(*t*) = max<sub>*s* ≤ *t*</sub> *P*(*s*). The reference level against which drawdown is measured.

## S

**S&P 500** *(Ch. 1)* — Index of the 500 largest U.S. public companies,
weighted by market capitalization. The most-watched gauge of the U.S. stock
market.

**Sample mean (*μ̂*)** *(Ch. 4)* — The arithmetic average of a finite sample
of observations: *μ̂* = (1/N) Σᵢ *rᵢ*. The natural estimator of the
population mean. Unbiased; standard error scales like 1/√N.

**Scale parameter σ (GPD)** *(Ch. 10 §2)* — The spread parameter of the Generalized Pareto Distribution. Always positive; same units as the exceedances being fit. Combined with ξ in the EVT-VaR formula.

**Shape parameter ξ (GPD)** *(Ch. 10 §2)* — The tail-heaviness parameter of the Generalized Pareto Distribution. **ξ > 0 = heavy tail** (Pareto-like; daily equity returns sit at ξ ≈ 0.15-0.25); ξ = 0 = exponential; ξ < 0 = bounded. The deciding diagnostic for "how heavy is this tail."

**Sklar's theorem** *(Ch. 10 §6, named only)* — Any joint distribution decomposes into its marginals plus a copula: F(x, y) = C(F<sub>X</sub>(x), F<sub>Y</sub>(y)). Lets you model marginals (e.g., GPD for tails) separately from dependence (e.g., t-copula).

**Second moment** *(Ch. 2)* — The variance of a distribution. Daily returns
are *not* second-moment-stationary — the rolling-vol plot is the proof.

**Sharpe ratio** *(Ch. 5)* — Mean excess return divided by excess-return volatility: *Sharpe* = *μ*<sub>excess</sub> / *σ*<sub>excess</sub>. The simplest risk-adjusted-return metric. Annualizes by **× √252** (not × 252) for daily data. Compare Sharpes only with their CIs (Ch. 5 §4.3) — they're noisier than the headline number suggests.

**Shrinkage** *(Ch. 4)* — Pulling a noisy estimate toward a prior to reduce
mean-squared error at the cost of a small bias. Applied to expected-return
estimates in Ch. 4; used in production portfolio construction in Ch. 6.

**Signal-to-noise ratio (SNR)** *(Ch. 4)* — The ratio of an estimate to its
standard error; equivalent to the t-statistic. Measures how confidently we
can distinguish the estimate from zero.

**Simple return** *(Ch. 1)* — `Pₜ / Pₜ₋₁ − 1`. The return number a brokerage
statement reports.

**Slope (*β̂*)** *(Ch. 7)* — The coefficient on a regressor in a linear regression: change in *y* per unit change in *x*, on average. In CAPM (Ch. 8), the slope of (asset − r<sub>f</sub>) on (market − r<sub>f</sub>) is the famous *β*.

**SMB (Small Minus Big)** *(Ch. 8)* — Size factor in Fama-French 3-factor model. Daily return of a portfolio long small-cap stocks and short large-cap stocks. Positive on days small caps beat large caps. Most sector ETFs have small-negative β<sub>SMB</sub> (large-cap-tilted by construction).

**Sortino ratio** *(Ch. 5, named only)* — A Sharpe variant that uses *downside-only* deviation in the denominator, so upside vol isn't penalized. Useful when return distributions are asymmetric.

**Spurious correlation** *(Ch. 7)* — Apparent regression relationship between unrelated series, often via shared trend. Two independent random walks regressed on each other produce |t| > 2 in 98% of trials with no causal relationship. Empirical fix: regress on *changes*, not *levels*. Genuine level-comovement is **cointegration** (named only).

**Split** *(Ch. 1)* — A re-denomination of a company's shares (e.g., 2-for-1:
each existing share becomes two shares of half the price). No economic value
changes; *adjusted close* corrects historical prices for splits.

**Standard deviation (σ)** *(Ch. 1)* — Square root of the *variance*. Same
units as the underlying data, which is why it's typically the dispersion
measure we report.

**Standard error (SE)** *(Ch. 4)* — The standard deviation of an estimator's
sampling distribution. For the sample mean: *SE(μ̂)* = *σ* / √N. **Annualize
by × 252** (same rule as the mean), not √252.

**Standardised residual** *(Ch. 9)* — *ε<sub>t</sub>* / *σ̂<sub>t</sub>* — observed return divided by GARCH-implied conditional volatility. Should be approximately i.i.d. unit-variance if the vol model captured everything. Diagnostic: ACF of squared standardised residuals should be flat near zero (vs raw squared returns, where it shows clear vol clustering).

**Structural break** *(Ch. 9 §7)* — Permanent shift in the data-generating process — e.g., the COVID jump in March 2020. GARCH assumes (ω, α, β) are constants over the fit window; structural breaks violate this assumption. Production response: refit on a rolling window, accept that parameters drift.

**Standard error of a coefficient** *(Ch. 7)* — The standard deviation of an OLS coefficient's sampling distribution. *SE(β̂)* = *σ̂<sub>ε</sub>* / √(Σ(x<sub>t</sub> − x̄)²). Same shape as Ch. 4's *SE(μ̂)*, applied to a slope. Drives the t-statistic and 95% CI on the coefficient.

**`statsmodels`** *(Ch. 7, named only)* — Python library providing OLS and other statistical models with full inference output (SEs, t-statistics, p-values, CIs). Convention: `import statsmodels.api as sm`.

**Stationarity** *(Ch. 2; revisited Ch. 9)* — A property of a time series whose statistical
properties (mean, variance, autocorrelation) don't change over time. Real
return series are at best approximately mean-stationary and clearly *not*
variance-stationary. **Conditional GARCH variance** is approximately stationary (α + β < 1 is the formal condition); standardised GARCH residuals approach i.i.d.-stationary, which is what makes filtered historical simulation (Ch. 10) work.

**Systematic risk** *(Ch. 3; formalized Ch. 8)* — The portion of risk that *can't* be
diversified away — common factor exposure shared across many assets.
Complement of *idiosyncratic risk*; formalized via factor models in later
chapters.

## T

**Tail dependence coefficient (λ<sub>U</sub>, λ<sub>L</sub>)** *(Ch. 3 named; Ch. 10 §5 formalized)* — Conditional probability of joint extreme: λ<sub>U</sub> = lim<sub>q→1</sub> P(Y > F<sub>Y</sub><sup>−1</sup>(q) | X > F<sub>X</sub><sup>−1</sup>(q)); λ<sub>L</sub> analogous in the lower tail. Range [0, 1]. Independence → 0; comonotone → 1. Empirical estimator: count joint exceedances. **Survives the truncation artifact that bit Ch3's conditional Pearson ρ.** Highlight finding from Ch. 10 §5.3: SPY/TLT Pearson ρ = −0.31 *but* λ̂_U = λ̂_L ≈ 0.05 — Pearson and tail-λ tell genuinely different stories.

**Tail premium** *(Ch. 5)* — The gap between historical VaR and Gaussian VaR; the quantitative restatement of Ch. 2's fat-tail finding. *Quantile-dependent*: ~1.0× at 5%, ~1.3× at 1%, ~1.5× at 0.5%. Fat tails are a divergence in *shape* in the deep tail, not a uniform multiplier.

**Tails** *(Ch. 1)* — The far-left and far-right ends of a distribution,
where rare extreme values live. See also *fat tails*.

**Tangency portfolio** *(Ch. 6)* — The point on the efficient frontier with the maximum Sharpe — equivalently, the portfolio whose ray from (0, *r<sub>f</sub>*) is tangent to the frontier. Unconstrained closed form: **w**<sub>tan</sub> ∝ **Σ**⁻¹ (**μ** − *r<sub>f</sub>***1**). The Σ⁻¹ in the formula is precisely what makes mean-variance unstable on noisy μ̂.

**t-copula** *(Ch. 10 §6)* — Copula induced by the multivariate-t distribution. Has *non-zero* tail dependence in both upper and lower tails (symmetric), unlike the Gaussian copula. Standard heavier-tailed alternative for modern multivariate-EVT applications; the t-copula CDO model would not have made the 2008 mistake.

**Threshold u** *(Ch. 10 §3)* — In peaks-over-threshold EVT, the cutoff above which exceedances are modelled by GPD. Picked from a mean-residual-life plot in the linear region. p95 of losses is a standard practical default for daily-equity work; threshold sensitivity should be checked across p80-p99.

**Two-fund separation theorem** *(Ch. 6, named only)* — Under mean-variance optimization with a risk-free asset, every Sharpe-maximizing investor holds some mix of *r<sub>f</sub>* and the **tangency portfolio**. Risk aversion determines the mix; risky composition is the same for everyone.

**T-bill** *(Ch. 5)* — Treasury bill: short-term US Treasury debt (4-, 13-, or 26-week maturities). The standard real-world proxy for "risk-free in dollar terms." Yfinance ticker `^IRX` reports the annualized 13-week T-bill yield in percent.

**t-statistic** *(Ch. 4; formal definition Ch. 7 §3)* — An estimate divided by its standard error.
Roughly, the number of standard errors away from zero. |t| > 2 is the
conventional threshold for "statistically distinguishable from zero." Approximately standard-normal under H₀ for large N. **A low bar in finance**: random walks regressed on each other clear |t| > 2 in 98% of trials (Ch. 7 Exercise 4).

**Ticker** *(Ch. 1)* — Short alphabetic symbol identifying a security on an
exchange (e.g., `SPY`, `AAPL`, `BRK-B`).

**Trading day** *(Ch. 1)* — A day on which the market in question is open.
For U.S. equities, there are roughly **252** per year (365 minus weekends and
~9 holidays).

## U

**Underwater curve** *(Ch. 5)* — A time-series plot of drawdown (*DD*(*t*) vs time). Visualizes how long the price path spent "submerged" below prior peaks; the shape conveys both depth and recovery.

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

**Volatility parity** *(Ch. 6, named only)* — Simpler cousin of risk parity that weights by 1/σ<sub>i</sub> ignoring correlations. Faster to compute and often comparable to ERC when correlations are low; differs meaningfully when there are strong cross-asset correlations.

**Value at Risk (VaR)** *(Ch. 5)* — A loss threshold: *VaR<sub>α</sub>* = − *Q<sub>α</sub>*(*r*). "5% VaR of 1.8%" means losses of at least 1.8% on 5% of days. Blind to tail shape past the threshold — pair with *CVaR*.

## Z

**ZIRP** *(Ch. 5)* — Zero-Interest-Rate Policy era when the risk-free rate sat near 0%. In US data: roughly late 2008–2015 and 2020–2021.

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
