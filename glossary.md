# Glossary

A running, alphabetical reference for every domain term used in this guide.
Each entry notes the chapter where the term is first introduced; consult that
chapter's prose for the term in context.

If you hit a term anywhere in the guide that isn't defined here, that's a bug
— please flag it.

> **Note on retired chapter references.** The curriculum was repivoted on
> 2026-05-07 from a portfolio/measurement track to an intraday-futures track.
> Glossary entries tagged *(Ch. 6)*, *(Ch. 7)*, *(Ch. 8)*, *(Ch. 9)*, or
> *(Ch. 10)* and originally written for **portfolio construction, regression,
> factor models, GARCH, or EVT/copulas** refer to the **retired chapters**.
> New entries first introduced in the post-pivot Ch6 onward use the same
> numeric chapter labels but cover different content. Where it matters for
> clarity, individual entries flag "(retired)" or "(intraday)".

---

## Numerals

**60/40 portfolio** *(Ch. 3)* — Canonical balanced allocation of 60% equities
(typically broad US equity) and 40% bonds (typically intermediate-to-long
Treasuries). The default "diversified" portfolio in retail and pension
contexts; works because the SPY/TLT correlation is typically negative.

## A

**ADV (Average Daily Volume)** *(Ch. 12)* — Typical daily traded volume of an instrument, usually quoted in dollars. Denominator of the square-root impact law: impact = η · σ<sub>d</sub> · √(Q/ADV). For ETFs, the consolidated-tape ADV across all 16 US equity venues can be ~30× larger than venue-specific ADV (e.g., IEX-only). Always use consolidated ADV when modeling realistic execution; QQQ's consolidated ADV in 2025-2026 is ~$15B.

**Adverse selection (toxicity)** *(Ch. 13)* — The systematic tendency for passive limit fills to occur exactly when the market is about to move against the posted side: limits get hit *because* an informed counterparty is crossing the spread. Quantified as `toxicity = drift_unconditional − drift_filled`, the wedge between the K-bar drift on the full signal universe and the K-bar drift on the subset that actually filled as passives. Positive toxicity → filled trades did worse than the strategy expected. The canonical microstructure reason why "post a limit instead of crossing the spread" doesn't trivially flip the sign of an after-cost Sharpe.

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

**Backtest** *(Ch. 8, intraday; rebuilt Ch. 9)* — A simulation of a trading strategy on historical data, used to estimate the strategy's PnL distribution before risking capital. **Vectorized backtests** compute PnL as a series of forward-return × signal products in one shot; **event-driven backtests** loop bar-by-bar with explicit position state and a trade ledger. Ch9's event-driven rebuild of Ch8's strategy roughly halved the in-sample Sharpe (+2.08 → +0.80) and surfaced a 95% bootstrap CI on the trade ledger of (−1.3, +2.7) — the kind of honest mechanics every later chapter inherits.

**Bar-boundary look-ahead** *(Ch. 9 §1, intraday)* — Specific look-ahead bug where the closing price of bar *t* appears both in the signal computation (its right edge) and in the executed return (its left edge), so the backtest fills at a price the trader never could have seen in real time. The most common bug in vectorized intraday backtests; on Ch8's QQQ MR strategy, removing it dropped the headline Sharpe from +1.57 to +0.80. The fix is a one-bar shift to a `next-open` fill assumption.

**Bar gap (intraday)** *(Ch. 6, intraday)* — A minute in a trading session that produces no bar in the data feed. On Alpaca's free-tier IEX feed, gaps are common (~2-3% of RTH minutes) and reflect minutes when no trade printed *on IEX specifically*, even if other venues had trades. Distinguish from a *short session* (real holiday early close) and a *vendor outage* (genuine data loss).

**Bear market** *(Ch. 1)* — A sustained market decline of roughly 20% or more
from a recent peak. The threshold is a convention, not a law.

**Bias** *(Ch. 4)* — The expected difference between an estimator's value and
the true population value it's trying to estimate. An *unbiased* estimator
has bias = 0. The sample mean is unbiased for the population mean.

**Black-Litterman** *(Ch. 6, named only)* — Bayesian framework that combines an equilibrium prior on expected returns with an investor's subjective views to produce a stable posterior used as MVO input. The standard institutional response to mean-variance instability when *r<sub>f</sub>*-based shrinkage isn't enough.

**Block bootstrap** *(Ch. 6)* — Bootstrap resampling that draws *blocks* of consecutive observations rather than single points, preserving short-horizon dependence (volatility clustering, autocorrelation). Block length is a hyperparameter; 21 days is a common default for daily financial data.

**Block maxima (BM)** *(Ch. 10 §2, named only)* — EVT flavor: divide data into non-overlapping blocks (e.g., calendar years), take the maximum in each, fit a GEV distribution to the resulting maxima. Pedagogically clean but wasteful — uses ~20 of 5,000 observations on annual blocks. **Peaks-over-threshold (POT) is the daily-return choice** instead.

**Bonferroni correction** *(Ch. 10 §4, intraday)* — Multiple-comparison correction that raises each test's α to α / *K* for *K* simultaneous tests; controls family-wise error rate at α. Conservative — uniformly less powerful than Holm — but easy to compute and the natural baseline. Ch10 §4 sweeps 21 thresholds; uncorrected critical |t| = 1.96 vs Bonferroni-corrected 3.04. The cost of having looked at K parameters scales as Φ⁻¹(1 − α/(2K)) — sub-logarithmic but real.

**Bias–variance tradeoff** *(Ch. 4)* — The principle that accepting a small
bias in an estimator can sometimes reduce its overall mean-squared error.
Underlies shrinkage estimators and a huge swath of statistics and ML.

**Bull market** *(Ch. 1)* — A sustained rally of roughly 20% or more from a
recent trough. Mirrors *bear market*.

**Breakout** *(Ch. 7, intraday)* — Strategy family that trades range expansion after a period of compression. Mechanism: stops cluster on both sides of the range; once the range breaks, stops on the wrong side cascade into market orders that amplify the move. Part information (new info justifies a new range) and part mechanical (stop-runs).

## C

**CPI (Consumer Price Index)** *(Ch. 6, intraday)* — The headline US inflation print, released monthly by the Bureau of Labor Statistics at 08:30 ET, in the pre-market session. Causes a sharp vol spike on the release minute that is partially absorbed pre-market and partially rolls into the 9:30 cash open.

**CAPM (Capital Asset Pricing Model)** *(Ch. 8)* — Single-factor regression model: R<sub>i,t</sub> − r<sub>f,t</sub> = α + β·(R<sub>mkt,t</sub> − r<sub>f,t</sub>) + ε<sub>i,t</sub>. The simplest factor model in finance; β captures market exposure and α captures the residual mean. Operationally a one-regressor OLS fit; the textbook normative derivation (utility, market clearing) is out of scope here.

**Capacity (strategy capacity, Q\*)** *(Ch. 12)* — Largest trade size at which a strategy's after-cost expectancy is non-negative. Q\* = ADV · ((μ<sub>trade</sub> − 2s − 2c) / (2 η σ<sub>d</sub>))² when the *impact budget* (μ<sub>trade</sub> − 2s − 2c) is positive; Q\* = $0 otherwise. A strategy with negative impact budget is unprofitable at any size — explicit costs alone exceed the per-trade edge. Ch12 finds Q\* = $0 for the closing-window MR strategy on QQQ at the cost-aware optimum k\* = 2.2.

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

**Corwin-Schultz estimator** *(Ch. 12)* — Estimator of the bid/ask spread from two-bar high-low ranges. Derives spread from the inflation of log(H/L) beyond what within-bar Brownian variance would predict, calibrated from the combined two-bar range γ. Independent of *Roll's estimator*; useful as a second-opinion sanity check. Published for daily bars; adaptation to 1-min bars works well on liquid ETFs but degrades on thinly-traded names. On QQQ 1-min, gives 0.79 bp half-spread vs Roll's 0.72 bp — agreement within 10%.

**Cost-aware optimization** *(Ch. 12)* — Re-tuning a strategy parameter with the *after-cost* performance as the objective. Distinct from cost-naive optimization (optimize pre-cost, subtract costs at the end). Cost-aware optima sit at higher thresholds and lower trade counts because cost is levied per trade. On Ch12's QQQ MR strategy, cost-naive k\* = 0.70 (S_pre +2.77) flips to cost-aware k\* = 2.20 (S_post = −2.97 — still negative, since costs exceed the per-trade edge at every threshold).

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

**Crowding** *(Ch. 7, intraday)* — Capacity-driven decay of an edge as more capital trades the same signal. Classic case: equity stat-arb / pairs trading, where Sharpes of 2-3 pre-2010 collapsed to 0.5-1 by mid-2010s as the strategy went mainstream.

## D

**Dollar bar** *(Ch. 6, intraday)* — A bar that closes whenever a fixed amount of notional dollar volume has traded. Equalizes information density across the day: more samples in the closing hour, fewer in the midday lull. Compare *time bar*, *volume bar*, *imbalance bar*. Reappears in Ch13 microstructure when slippage modeling needs information-equalized samples.

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

**Deflation factor** *(Ch. 11 §1, intraday)* — Ratio of out-of-sample Sharpe to in-sample Sharpe: OOS / IS. Captures the strategy's signal-to-noise ratio under honest evaluation. Typical retail strategies deflate to 0.3-0.7. On Ch11's QQQ closing-window MR strategy, train/test split deflation = 0.28 (severe); above 0.7 is suspicious (suggests accidental information leakage); at 0 means the IS was noise.

## E

**ETH (Extended Trading Hours)** *(Ch. 6, intraday)* — Pre-market (~04:00–09:30 ET) and after-hours (~16:00–20:00 ET) trading on US equity venues. Thinner liquidity, wider spreads, gappier prints than RTH. This curriculum mostly operates RTH-only; sub-session strategies rarely benefit from ETH given the liquidity penalty.

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

**Explicit cost** *(Ch. 12)* — Costs that hit the brokerage statement: commission, exchange fees, SEC fees, financing on margin and overnight inventory. Visible, billed, easy to model. For QQQ retail, on the order of 0.05-0.07 bp per leg at IBKR tiered; $0 at PFOF-funded brokers (Schwab/Fidelity/Robinhood). Contrast with *implicit cost*.

**Excess kurtosis** *(Ch. 2)* — Kurtosis minus 3, so the normal-distribution
benchmark equals zero. Positive values mean tails heavier than the normal
predicts.

**Excess return** *(Ch. 5)* — Asset return minus the risk-free rate: *r*<sub>excess,t</sub> = *r<sub>t</sub>* − *r*<sub>f,t</sub>. The compensation for taking risk; the input to Sharpe-style metrics. Earning the risk-free rate isn't compensation for risk — you could have it without taking any.

**Execution timing** *(Ch. 9 §3, intraday)* — The choice of *which* bar's *which* price counts as the fill in a backtest. Three canonical timings: **same_close** (entry/exit at the close of the signal/exit bar — Ch8's bug), **next_open** (entry/exit at the open of the bar after the signal/exit bar — the cleanest defensible point-in-time rule), **next_close** (one bar later than next_open — a coarse one-bar-slippage proxy that doesn't bite at 1-minute resolution).

**Expected Shortfall (ES)** *(Ch. 5)* — Synonym for **Conditional VaR (CVaR)**.

**Expected value (*E*[·])** *(Ch. 2)* — The average of the bracketed quantity
over the data. For a sample of *n* observations, *E*[*x*] = (*x*<sub>1</sub> +
… + *x<sub>n</sub>*) / *n* — the same operation as the *mean*. The bracket
notation lets us cleanly write averages of more complex expressions, like
*E*[(*X* − *μ*)²] for variance or *E*[(*X* − *μ<sub>X</sub>*)(*Y* −
*μ<sub>Y</sub>*)] for covariance.

**Edge** *(Ch. 7, intraday)* — The only operational definition: positive expectancy per trade *after costs*, in some defined regime. Every other definition you'll hear ("high win rate," "great Sharpe," "consistent profit factor") either implies expectancy or fails to capture it. Edges are conditional, not universal; they decay.

**Event-driven** *(Ch. 7, intraday)* — Strategy family that trades around scheduled news (FOMC, CPI, NFP, earnings). Mechanism: scheduled releases create an *expected* variance window — the market knows information is arriving at a specific time, so vol is structurally elevated for some minutes around the print. The vol regime is the predictable part; direction is usually a separate, harder problem.

**Event-driven backtest** *(Ch. 9 §2, intraday)* — A backtest that loops bar-by-bar through the data, maintaining explicit position state and processing entries and exits as they would occur in real time. Slower to write than a vectorized backtest but harder to get *wrong* in subtle ways — execution timing, position management, and order-of-operations are coded explicitly rather than buried in array math. The form every later chapter in the curriculum inherits. Distinct from *event-driven* (Ch7), which is the strategy-family name.

**Expectancy** *(Ch. 7, intraday)* — Per-trade expected value: *E* = *p* · *w* − (1 − *p*) · *l*, where *p* = hit rate, *w* = average winning trade, *l* = average losing trade (as positive number). *E* > 0 → strategy makes money in expectation; *E* after costs is the only quantity that decides profit.

## F

**Fill-or-kill (FOK)** *(Ch. 13)* — Order type that must be filled in its entirety immediately or cancelled entirely. No partial fills. Used when partial execution would compromise the strategy (e.g., a multi-leg trade where one leg without the others is a different position).

**Fill rate** *(Ch. 13)* — Fraction of would-be passive trades that successfully fill within the strategy's hold window: `filled / total_signals`. The denominator is the count of signals the strategy emitted; the numerator is the count whose limit was touched-through within K bars. Conditional metric — fill rate without the adverse-selection diagnostic alongside it overstates passive execution's value.

**FOMC (Federal Open Market Committee)** *(Ch. 6, intraday)* — The committee within the Federal Reserve that sets the US federal-funds-rate target. ~8 scheduled meetings per year, with the announcement at 14:00 ET. Causes a sharp vol spike on the announcement minute (~4-5× the same-time vol on a typical day on QQQ). One of the canonical "scheduled events" that drive intraday-strategy regime shifts.

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

**Fill assumption** *(Ch. 9 §1, intraday)* — The rule that converts a *decision* (the signal said "buy") into an *execution price* (you actually paid X). Common fill assumptions: **same_close** (fill at the close of the signal bar — usually wrong unless the order was placed before the close), **next_open** (fill at the open of the bar after the signal — the simplest defensible choice for an end-of-bar signal), **VWAP-of-next-K-minutes** (more realistic for sized orders), **midquote** (a finer assumption usable when bid/ask are available). The fill assumption is one input to the broader *execution-timing* choice.

**Filtered historical simulation (FHS)** *(Ch. 10 §3.4; named in Ch. 9 §5)* — Production-grade tail-VaR construction: standardise returns by GARCH σ̂<sub>t</sub>, fit EVT-GPD on the standardised residuals, recombine today's σ̂<sub>T</sub> with the residual tail-shape. **GARCH for the variance, EVT for the tail shape.** ξ̂ on standardised residuals (≈0.06 for SPY) is much smaller than ξ̂ on raw returns (≈0.19) — GARCH absorbs most of the fat-tail behavior.

**Fitted value** *(Ch. 7)* — The model's prediction at an observed *x*: *ŷ<sub>t</sub>* = *α̂* + *β̂*·*x<sub>t</sub>*. The y-coordinate of the regression line at *x<sub>t</sub>*. The *residual* is observed minus fitted.

**Forecast / conditional expected return** *(Ch. 4)* — Expected return *given
current state* — a prediction that varies day-to-day, in contrast to the
long-run unconditional mean. Named in Ch. 4 as a deferred flavor; formalized
in Ch. 8 and Ch. 11–12.

**Fakeout** *(Ch. 7, intraday)* — A breakout that reverses immediately after triggering the initial wave of stops. Market-making firms know exactly where retail stops sit; when the post-break move can't sustain itself on real flow, the original range tends to reassert and the breakout traders are stopped out at a loss.

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

**Half-spread** *(Ch. 12)* — Half the inside bid/ask spread, expressed as a fraction of price or in bp. The one-leg cost of crossing the spread once — buying at the ask or selling at the bid instead of executing at the mid. Round-trip transactions cross the spread twice, so round-trip spread cost ≈ 2 · half-spread. On QQQ 1-min in 2025-2026, Roll's estimator gives ~0.72 bp all-RTH.

**Hidden factor exposure** *(Ch. 3; paid Ch. 8 §5)* — The phenomenon that seemingly distinct
assets share underlying drivers (interest rates, oil, the broad market
itself), so a "diversified" portfolio may be a single bet. Quantified in Ch. 8 by computing the basket's weighted-average β: EW8 over the curriculum's 8-ticker basket has β ≈ 0.69 and R² on SPY ≈ 0.90 — *the basket is essentially a one-factor object.*

**HML (High Minus Low)** *(Ch. 8)* — Value factor in Fama-French 3-factor model. Daily return of a portfolio long high-book-to-market (value) stocks and short low (growth) stocks. Positive on days value beats growth. XLF loads strongly positive (banks are value); XLK loads strongly negative (tech is growth).

**Heteroskedasticity** *(Ch. 7)* — Residual variance that depends on *x* (or on time). Breaks the textbook OLS standard-error formulas, which assume constant residual variance (*homoskedasticity*). Diagnosed via residuals-vs-fitted plot (fan shape); partly fixed by HAC SEs.

**Histogram** *(Ch. 1)* — A bar chart that buckets observations into ranges
(*bins*) and draws a bar whose height shows how many observations fall in
each bin. The visual representation of an empirical distribution.

**Historical VaR** *(Ch. 5)* — VaR computed empirically as a quantile of the observed return distribution: *VaR<sub>α</sub>* = − *Q<sub>α</sub>*(*r*). No distributional assumption. Preferred to Gaussian VaR for daily equity tails at α ≤ 1% (where the fat-tail premium materially bites).

**Hit rate** *(Ch. 7, intraday)* — Fraction of trades closed at a profit (before costs). Synonym: *win rate*. Meaningless alone — must be paired with *payoff ratio* to compute *expectancy*. A 0.70 hit rate with a 0.30 payoff has expectancy −0.09*R* per trade.

**Holding period** *(Ch. 8, intraday)* — The number of bars (or wall-clock units) a position is held between entry and exit. Often denoted *K* in this curriculum's strategy notation. Choosing *K* is a free parameter that interacts with the lookback *N*: shorter *K* harvests fast mean-reversion; longer *K* averages over more noise.

**Holm-Bonferroni correction** *(Ch. 10 §4, intraday)* — Stepwise multiple-comparison correction. Sort the *K* p-values ascending; compare the *i*-th smallest to α / (*K* − *i* + 1). Uniformly more powerful than plain Bonferroni — accepts any subset Bonferroni accepts, sometimes more — with the same family-wise error guarantee. On Ch10's 21-threshold sweep, neither correction passes anything (best uncorrected |t| = 1.84 fails even the standard 1.96 bar).

## I

**Immediate-or-cancel (IOC)** *(Ch. 13)* — Order type that fills whatever can fill immediately at the limit price and cancels any unfilled remainder. Prevents the order from resting on the book and leaking strategy information after the moment of execution. Useful for signal-driven strategies that don't want to be hit later.

**IEX feed** *(Ch. 6, intraday)* — Trade prints from IEX (Investors Exchange), one US equity venue. The free tier of Alpaca's Market Data API delivers IEX-only minute bars. Compare *SIP* (the consolidated full-tape feed across all venues, paid). Has gaps — minutes when IEX itself had no print but other venues did produce no bar at all (~2-3% of RTH minutes typically missing on QQQ).

**Impact (market impact)** *(Ch. 12)* — The adverse price move caused by your own order eating through the resting book. Modeled by the *square-root impact law*: impact = η · σ<sub>d</sub> · √(Q/ADV), in fractional units. Empirically robust across markets, with η ≈ 0.1 for liquid US equities. For retail-sized trades on QQQ ($10k-$100k), impact is well below half-spread; impact only dominates at $10M+ institutional size.

**Implicit cost** *(Ch. 12)* — Costs paid through prices, not the brokerage statement: the bid/ask spread you cross on entry and exit, and the slippage / market impact your size induces. Invisible on the statement; first-order on small-edge strategies. Contrast with *explicit cost*.

**Imbalance bar** *(Ch. 6 §3, named only)* — A bar that closes whenever signed order-flow imbalance (buy volume minus sell volume) crosses a fixed threshold. Equalizes by *information arrival* in the microstructure sense. Most exotic of the four standard bar types; needs trade-direction inference (Lee-Ready or similar). See López de Prado, *Advances in Financial Machine Learning* (2018), Ch. 2.

**Intraday seasonality** *(Ch. 6, intraday)* — Time-of-day structure in any session-stationary statistic (vol, volume, spread). The headline example is the *U-shape* in mean absolute return, with elevated vol at the open and (sometimes) the close vs the midday lull.

**Idiosyncratic risk** *(Ch. 3; formalized Ch. 8 §2)* — The asset-specific portion of risk that
can be diversified away in a sufficiently large basket — the residual ε in a factor-model regression. Complement of *systematic risk*.

**Intercept (*α̂*)** *(Ch. 7)* — The constant term in a linear regression: the average of *y* when *x* = 0. In CAPM-style regressions, the intercept of (asset − r<sub>f</sub>) on (market − r<sub>f</sub>) is the famous *α* — "everything not explained by market exposure" (Ch. 8).

**Holdout set** *(Ch. 11 §2, intraday)* — Synonym for the test set in a train/test split — the portion of the data the strategy and its parameters are *never* fit to. Operational rule: evaluate on the holdout exactly once. Iterate on the holdout — re-tune after seeing OOS performance — and you have effectively re-merged train and test, with all the snooping that implies.

**In-sample (IS)** *(Ch. 8, intraday; formalized Ch. 10)* — A metric computed on the same data used to choose the strategy's parameters. Always optimistic vs the truth; quote as an *upper bound* on what the strategy can really do. The Ch10 §4 sweep makes the upper-bound nature concrete — the best Sharpe across 21 thresholds is +1.86 but its t-statistic (1.84) fails even uncorrected significance. Compare *out-of-sample* (Ch11).

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

**Latency (signal-to-fill)** *(Ch. 13)* — Wall-clock time between the signal logic emitting an order and the exchange matching engine processing it. Components: signal compute, network RTT to broker, broker routing, exchange matching, response RTT. Random-walk-regime cost: σ<sub>drift</sub> = σ<sub>1min</sub> · √(Δt/60s); E\|drift\| ≈ 0.80 σ<sub>drift</sub>. Resolution-dependent: at 1-min/100ms latency drift is ~4% of bar σ (invisible); at 1-sec/200ms it's ~45% (dominant). Order-of-magnitude reference: co-located HFT < 1ms; cloud retail bot 5-50ms; retail desktop 50-500ms.

**Lag (*k*)** *(Ch. 2)* — The number of periods by which a series is shifted
when computing autocorrelation.

**Lookback** *(Ch. 8, intraday)* — The number of bars (or wall-clock units) of history fed into a signal computation. Often denoted *N* in this curriculum's strategy notation. *N* = 1 with QQQ closing-window minute returns harvests Ch7's lag-1 mean-reversion most cleanly.

**Limit order** *(Ch. 13)* — A standing instruction to buy at price *p* or lower (or sell at *p* or higher). If posted away from the inside touch, it joins the book and the trader becomes the *maker*; the fill is conditional (it executes only if a counterparty crosses the spread to your price). Trades the certainty of a market order for a price floor/ceiling and a chance at the maker rebate.

**Least squares** *(Ch. 7)* — The procedure of fitting a line (or hyperplane) by minimising the sum of squared residuals: SS(α, β) = Σ (y<sub>t</sub> − α − β·x<sub>t</sub>)². Closed-form solutions: *β̂* = Cov(x, y) / Var(x), *α̂* = ȳ − β̂·x̄.

**Long-run / unconditional vol** *(Ch. 9)* — Under GARCH(1,1), σ̄ = √(ω/(1−α−β)) is the steady-state vol the process mean-reverts to. For SPY 20y, σ̄ ≈ 18% annualized — close to the whole-sample sample σ ≈ 19.5%, sanity-checking the model.

**Log-likelihood** *(Ch. 9 §3.2)* — Sum of log-densities of observations under a parametric model. MLE picks parameters that maximise the log-likelihood. For GARCH with conditional Gaussian innovations: log L = −½ Σ [log σ²<sub>t</sub> + ε²<sub>t</sub>/σ²<sub>t</sub>].

**Look-ahead bias** *(Ch. 7; worked example Ch. 10 §2)* — Using information from time *t+1* (or later) to compute a feature or target at time *t*. The procedural fix: every feature available at *t* must be derivable strictly before *t*. **Pedagogically important course-correction from Ch10:** look-ahead can move Sharpe in *either* direction, not just inflate it. On Ch9's QQQ MR strategy, the whole-sample-σ threshold produced Sharpe +0.82 while the point-in-time trailing-σ version produced +1.64 — the trailing version adapts to local volatility regimes. The bug is using information you didn't have, regardless of inflation direction.

**Ledoit-Wolf shrinkage** *(Ch. 6, named only)* — Shrinkage estimator for the covariance matrix Σ̂, the analog of Ch. 4's James-Stein shrinkage on μ̂. Pulls Σ̂ toward a structured target (typically the diagonal) by a data-driven amount. Reduces the off-diagonal noise that Σ⁻¹ otherwise amplifies.

**Long-only constraint** *(Ch. 6)* — Optimization restriction *w*<sub>i</sub> ≥ 0 — no short selling. Acts as a statistical regularizer on top of its business meaning: caps the levering effect of Σ⁻¹ on noisy μ̂, often at near-zero vol cost on diversified baskets.

**Leptokurtic** *(Ch. 2)* — Technical adjective for "fat-tailed": having
excess kurtosis greater than zero.

**Log return** *(Ch. 1)* — The natural logarithm of the price ratio between
two periods: `ln(Pₜ / Pₜ₋₁)`. Log returns *add* across periods, which makes
multi-period math simpler.

## M

**Maker** *(Ch. 13)* — The liquidity-providing side of a trade: the resting limit order on the book that a taker hits. Earns the maker rebate (~$0.0020-$0.0030/share on tier-1 US equity venues). A passive limit posted away from the inside touch becomes a maker order; a marketable limit (already at-or-through the touch) is a taker.

**Maker rebate** *(Ch. 13)* — Per-share credit paid by an exchange to the maker (passive liquidity provider). NASDAQ tier-1 ≈ $0.0030/share. On QQQ at ≈ $695/share that's 0.043 bp per maker leg — small, but non-zero, and only available to non-marketable limit fills. A tiebreaker on near-breakeven strategies; insufficient to rescue a structurally cost-dominated strategy.

**Market order** *(Ch. 13)* — A standing instruction to buy or sell *now* at the best available price. Crosses the spread; the trader is the *taker*. Fill is near-guaranteed; price is not — on a thin book the order may walk through several levels. The instrument that pays the spread in exchange for execution certainty.

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

**Multiple-comparisons problem** *(Ch. 10 §4, intraday)* — The statistical fact that *K* simultaneous α-level tests have family-wise false-positive rate ≈ *Kα*, not α. Running 20 backtests with parameter sweeps means even random data produces an "edge" with probability ~64% at the standard 0.05 bar. Corrections: **Bonferroni** (raise each test's bar to α/*K*) and **Holm-Bonferroni** (stepwise). The deeper response is procedural: *don't quote in-sample sweep results as edges*; reserve in-sample sweeps for prototyping.

**Mean reversion** *(Ch. 7, intraday)* — Strategy family that fades overshoots back toward fair value. Mechanism: liquidity providers (market makers, HFT) earn the spread plus the small reversion that follows when price moves away from fair value faster than information justifies. Dominant intraday dynamic in liquid instruments. On QQQ this curriculum's headline finding is lag-1 ρ ≈ −0.028 across all RTH and ≈ −0.067 in the closing 30 minutes.

**Momentum** *(Ch. 7, intraday)* — Strategy family that trades the persistence of moves. Mechanism: information diffuses slowly; large institutional orders are sliced over hours/days to minimize market impact, keeping price moving in the direction of the order; behavioral biases (anchoring, FOMO) reinforce. Lives at horizons of hours to days on liquid ETFs; **harder to find at sub-session horizons** (which is why Ch8's first runnable strategy is mean-reversion, not momentum).

## N

**NFP (Non-Farm Payrolls)** *(Ch. 6, intraday)* — The headline US labor-market print from the BLS Employment Situation report, released monthly at 08:30 ET in the pre-market session. Like CPI, causes a sharp vol spike on the release minute that partially absorbs pre-market and partially rolls into the 9:30 cash open.

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

**Out-of-sample (OOS)** *(Ch. 11, intraday)* — Performance computed on data the strategy has never seen — neither during parameter selection nor during any "this looks reasonable" iteration. Lower-variance estimator of truth than IS; the only honest answer to "what does the strategy give us?" The walk-forward concat OOS Sharpe with bootstrap CI is the chapter's headline statistic.

**Parameter stability** *(Ch. 11 §3, intraday)* — Diagnostic from walk-forward optimization: does the in-sample-best parameter look similar across consecutive refits? Stable optimizers indicate real edges (parameters drift slowly with regime); unstable optimizers (3×+ swings between windows) are fitting per-window noise. On Ch11's data, k_σ ranged 0.7-2.5 across 10 walk-forward windows — clearly unstable.

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

**Point-in-time** *(Ch. 9 §1, intraday)* — Discipline that, at each instant *t* of a backtest, only data observable strictly *before* time *t* is allowed to inform decisions made at time *t*. A point-in-time-correct signal at close[*t*] uses no information from times ≥ *t*. Vectorized backtests have to enforce this with explicit lags; event-driven backtests enforce it by the order in which the loop processes bars. Violating point-in-time on Ch8's strategy roughly doubled the headline Sharpe.

**Price series** *(Ch. 1)* — A sequence of an asset's prices indexed by time
(typically one observation per trading day for daily data). The starting
primitive of nearly every quant analysis.

**Prior** *(Ch. 4)* — The target value toward which a shrinkage estimator
pulls. Common choices: the cross-sectional mean of all assets being shrunk,
or zero.

**Prediction interval** *(Ch. 7)* — Error bar on a *new individual ŷ*, computed as ŷ ± 1.96 · √(σ̂²<sub>ε</sub> + SE_line(x)²). Wider than the CI on the regression line because it includes the irreducible residual scatter on top of line-fitting uncertainty.

**p-value** *(Ch. 4; formal definition Ch. 7 §3)* — Probability of seeing |t| (or any test statistic) at least this large under the null hypothesis. p < 0.05 is the conventional reject-the-null bar; *low* in finance because we test many things — Ch. 7 Exercise 4 shows random walks clear |t| > 2 in 98% of trials.

**Parameter drift** *(Ch. 7, intraday)* — Edge decay where a strategy's fitted parameters become miscalibrated as the underlying regime changes — same family, same mechanism, but the specific lookback window or entry threshold no longer matches current conditions. The most insidious decay; Ch10/Ch11 (backtesting bias and walk-forward) is largely about not mistaking parameter drift for a real edge.

**Parameter sweep** *(Ch. 10 §4, intraday)* — A grid of parameter values evaluated on the same data, often as a prelude to selecting "the best" one. The order statistic of K noisy estimates is, by construction, larger than any individual estimate's mean — so sweep-best Sharpe is always an upper bound, never the strategy's actual edge. The natural object for Bonferroni-style corrections; the natural object for OOS validation in Ch11.

**Payment for order flow (PFOF)** *(Ch. 12)* — Compensation arrangement where a retail broker routes its customers' orders to a wholesale market maker (Citadel, Virtu) instead of public lit exchanges. The wholesaler pays the broker a fraction of a cent per share for the flow; customers receive some price improvement vs the NBBO. Enables "zero commission" retail trading; shifts cost into the spread the wholesaler captures. Operationally invisible to the retail trader but a real cost.

**Payoff ratio** *(Ch. 7, intraday)* — *R*<sub>p</sub> = avg_win / avg_loss. Measures how big winners are relative to losers in payoff units. Trend / breakout strategies tend to have low hit rate / high payoff; mean-reversion strategies tend to have high hit rate / low payoff. Both are viable; both can be unprofitable depending on the multiplication.

**Profit factor** *(Ch. 7, intraday)* — gross_winnings / gross_losses. PF > 1 is profitable; PF > 2 is strong; **PF > 3 over a long sample raises curve-fit suspicion** — real strategies on liquid instruments rarely sustain this over thousands of trades.

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

**RTH (Regular Trading Hours)** *(Ch. 6, intraday)* — 09:30 AM – 4:00 PM ET on weekdays — the main US equity cash session. The default session for sub-session strategies in this curriculum. Compare *ETH* (extended trading hours).

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

**Regime change** *(Ch. 7, intraday)* — The transition *event* between two regimes (vol regime, correlation regime, etc.) that switches edges on or off. Distinct from *regime* (Ch2): regime is the state, regime change is the transition. A mean-reversion strategy fit during low vol can fail when vol regime-shifts upward — the strategy isn't worse, the conditions changed. Ch15 (intraday vol & regime detection) is about catching these transitions in real time.

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

**Roll's estimator** *(Ch. 12)* — Estimator of the effective half-spread from trade-price returns: *s* = √(−Cov(*r<sub>t</sub>*, *r<sub>t−1</sub>*)) when the lag-1 covariance is negative. Mechanism: under random bid-ask-bounce, consecutive trade returns gain a mechanical negative autocovariance equal to −s². Gives an *upper bound* on true spread because it cannot tell genuine mean-reversion apart from bid-ask noise. The Ch7 lag-1 ρ and Roll's estimator measure the same statistic, rescaled. Ch12 finds Roll's all-RTH = 0.72 bp on QQQ.

**Rolling correlation** *(Ch. 3)* — Pairwise correlation computed over a
sliding window of recent observations. Reveals time-variation that a
single-number long-run correlation hides — e.g., the SPY/TLT correlation
flipping signs across regimes.

**Rolling window** *(Ch. 2)* — A sliding subset of a time series used to
compute a statistic at each point in time. A rolling-window standard deviation
visualizes how volatility changes through time.

**Running peak** *(Ch. 5)* — The maximum of a price series up to and including time *t*: *P*<sub>peak</sub>(*t*) = max<sub>*s* ≤ *t*</sub> *P*(*s*). The reference level against which drawdown is measured.

## S

**Session boundary** *(Ch. 6, intraday)* — The transition between session N's close and session N+1's open. For sub-session strategies (this curriculum's target), mostly "ignore" — strategies are flat by close. For swing strategies (out of scope), the overnight gap is its own risk to model.

**SIP (Securities Information Processor)** *(Ch. 6, intraday)* — The consolidated full-tape feed across all US equity venues — every trade, every quote update. Available from data vendors as a paid product. The IEX-only free-tier feed used in this curriculum is a subset.

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

**Signal** *(Ch. 8, intraday)* — The numerical output of a strategy's decision rule at a given bar — typically a desired position size or direction. The Ch8 signal is `−sign(prior_1min)` when |prior_1min| > 1.0σ, else 0.

**Single-position rule** *(Ch. 9 §2, intraday)* — Position-management rule that allows at most one open trade per side at a time. Drops overlapping signals (a signal that fires while a trade is already open is ignored). The realistic default in a single-account backtest. Ch8's vectorized PnL did *not* enforce single-position — it summed every signal-bar's `signal × forward_return` contribution, which counts overlapping trades as separate "trades." The single-position event-driven version of Ch8's strategy produced 914 trades vs Ch8's 1,471, on identical data.

**Simple return** *(Ch. 1)* — `Pₜ / Pₜ₋₁ − 1`. The return number a brokerage
statement reports.

**Slope (*β̂*)** *(Ch. 7)* — The coefficient on a regressor in a linear regression: change in *y* per unit change in *x*, on average. In CAPM (Ch. 8), the slope of (asset − r<sub>f</sub>) on (market − r<sub>f</sub>) is the famous *β*.

**SMB (Small Minus Big)** *(Ch. 8)* — Size factor in Fama-French 3-factor model. Daily return of a portfolio long small-cap stocks and short large-cap stocks. Positive on days small caps beat large caps. Most sector ETFs have small-negative β<sub>SMB</sub> (large-cap-tilted by construction).

**Square-root impact law** *(Ch. 12)* — Empirical regularity that the temporary price impact of a market order scales as the square root of the order's fraction of average daily volume: impact = η · σ<sub>d</sub> · √(Q/ADV). η ≈ 0.1 for liquid US equities (Almgren et al. 2005); 0.3 conservative; 0.5 microcap territory. The √ exponent reflects the fact that doubling order size doesn't double impact — liquidity refreshes between marginal fills. Robust across markets and decades of TAQ studies.

**Slippage** *(Ch. 9 §3, intraday)* — Difference between the price implied by the signal and the actual fill price you receive. Costs (spread, commission), partial fills, and price drift between the decision and the execution all contribute. Ch9 uses a `next_close` execution timing as a coarse proxy but finds it ≈ `next_open` at 1-minute bar resolution (intra-bar drift is small). Realistic slippage modeling needs an explicit cost function — the topic of Ch12.

**Sortino ratio** *(Ch. 5, named only)* — A Sharpe variant that uses *downside-only* deviation in the denominator, so upside vol isn't penalized. Useful when return distributions are asymmetric.

**Snooping bias** *(Ch. 10 §4, intraday)* — Inflation of measured performance caused by selecting one parameter (or model variant) from many candidates evaluated on the same data. Synonyms: *data mining bias*, *p-hacking*. Mechanically identical to the multiple-comparisons problem applied to backtesting. Headline finding on Ch10's 21-point sweep: best in-sample Sharpe (+1.86) versus median across the sweep (+0.82) — a 1.04 Sharpe gap that is *entirely* an artifact of having looked at 21 thresholds.

**Survivorship bias** *(Ch. 10 §3, named-only, intraday)* — Backtest universe that excludes failed/delisted entities, so only survivors are in-sample. Inflates measured returns by 1-2% annualized on US equity universes per published research. Essentially absent for our QQQ-based curriculum (the ETF wrapper absorbs constituent rebalances internally) but bites hard on stock-picking strategies. Survivorship-clean data sources: CRSP (academic gold standard), Norgate Data (~$50/month retail), Sharadar (mid-tier).

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

**Taker** *(Ch. 13)* — The liquidity-removing side of a trade: a market order or marketable limit that crosses the spread and lifts a resting limit. Pays the taker fee (~$0.0030/share on tier-1 US equity venues), pays the spread, and gets immediate execution. The complement of *maker*.

**Toxicity** *(Ch. 13)* — See *Adverse selection*.

**Time bar** *(Ch. 6, intraday)* — A bar covering a fixed wall-clock interval (e.g. 1 minute, 5 minutes). The default sampling for most quant work; constant cadence; varying information density across the session. Compare *volume bar*, *dollar bar*, *imbalance bar*.

**Tail dependence coefficient (λ<sub>U</sub>, λ<sub>L</sub>)** *(Ch. 3 named; Ch. 10 §5 formalized)* — Conditional probability of joint extreme: λ<sub>U</sub> = lim<sub>q→1</sub> P(Y > F<sub>Y</sub><sup>−1</sup>(q) | X > F<sub>X</sub><sup>−1</sup>(q)); λ<sub>L</sub> analogous in the lower tail. Range [0, 1]. Independence → 0; comonotone → 1. Empirical estimator: count joint exceedances. **Survives the truncation artifact that bit Ch3's conditional Pearson ρ.** Highlight finding from Ch. 10 §5.3: SPY/TLT Pearson ρ = −0.31 *but* λ̂_U = λ̂_L ≈ 0.05 — Pearson and tail-λ tell genuinely different stories.

**Tail premium** *(Ch. 5)* — The gap between historical VaR and Gaussian VaR; the quantitative restatement of Ch. 2's fat-tail finding. *Quantile-dependent*: ~1.0× at 5%, ~1.3× at 1%, ~1.5× at 0.5%. Fat tails are a divergence in *shape* in the deep tail, not a uniform multiplier.

**Tails** *(Ch. 1)* — The far-left and far-right ends of a distribution,
where rare extreme values live. See also *fat tails*.

**Tangency portfolio** *(Ch. 6)* — The point on the efficient frontier with the maximum Sharpe — equivalently, the portfolio whose ray from (0, *r<sub>f</sub>*) is tangent to the frontier. Unconstrained closed form: **w**<sub>tan</sub> ∝ **Σ**⁻¹ (**μ** − *r<sub>f</sub>***1**). The Σ⁻¹ in the formula is precisely what makes mean-variance unstable on noisy μ̂.

**t-copula** *(Ch. 10 §6)* — Copula induced by the multivariate-t distribution. Has *non-zero* tail dependence in both upper and lower tails (symmetric), unlike the Gaussian copula. Standard heavier-tailed alternative for modern multivariate-EVT applications; the t-copula CDO model would not have made the 2008 mistake.

**Threshold u** *(Ch. 10 §3)* — In peaks-over-threshold EVT, the cutoff above which exceedances are modelled by GPD. Picked from a mean-residual-life plot in the linear region. p95 of losses is a standard practical default for daily-equity work; threshold sensitivity should be checked across p80-p99.

**Train/test split** *(Ch. 11 §2, intraday)* — Single partition of the data into a `train` portion (used for parameter selection) and a `test`/`holdout` portion (held out for OOS evaluation). The simplest validation procedure; honest if the test set is evaluated exactly once. Compare *walk-forward optimization* — repeated train/test in chronological sliding-window form.

**Two-fund separation theorem** *(Ch. 6, named only)* — Under mean-variance optimization with a risk-free asset, every Sharpe-maximizing investor holds some mix of *r<sub>f</sub>* and the **tangency portfolio**. Risk aversion determines the mix; risky composition is the same for everyone.

**T-bill** *(Ch. 5)* — Treasury bill: short-term US Treasury debt (4-, 13-, or 26-week maturities). The standard real-world proxy for "risk-free in dollar terms." Yfinance ticker `^IRX` reports the annualized 13-week T-bill yield in percent.

**Walk-forward optimization** *(Ch. 11 §3, intraday)* — Repeated train/test splits in chronological sliding-window form. At each step: refit on a trailing window (e.g., 3 months); evaluate on the next window (e.g., 1 month); slide forward one step. Concatenate the OOS evaluations into a single PnL series. Yields a continuously-OOS performance estimate plus a sequence of parameter choices whose stability is itself diagnostic. The honest way to estimate forward-looking strategy performance from a single fixed dataset.

**t-statistic** *(Ch. 4; formal definition Ch. 7 §3)* — An estimate divided by its standard error.
Roughly, the number of standard errors away from zero. |t| > 2 is the
conventional threshold for "statistically distinguishable from zero." Approximately standard-normal under H₀ for large N. **A low bar in finance**: random walks regressed on each other clear |t| > 2 in 98% of trials (Ch. 7 Exercise 4).

**Ticker** *(Ch. 1)* — Short alphabetic symbol identifying a security on an
exchange (e.g., `SPY`, `AAPL`, `BRK-B`).

**Trading day** *(Ch. 1)* — A day on which the market in question is open.
For U.S. equities, there are roughly **252** per year (365 minus weekends and
~9 holidays).

**Time-horizon dual** *(Ch. 7, intraday)* — The principle that the same return series can be mean-reverting at one timescale and trending at another. QQQ minute returns are anti-correlated at lag 1 (mean-reversion) and weakly positively correlated at lag 120 (early trend). "Is this asset mean-reverting or trending?" is the wrong question; "at what horizon, in what regime?" is the right one.

**Trend following** *(Ch. 7, intraday)* — A subset of momentum framed by directional persistence rather than signal-based entry. Classic implementation: enter when a moving-average crossover or breakout-of-N-day-high signals direction; exit on the reverse signal or trailing stop. Same mechanism as momentum (slow info diffusion + sliced execution).

**Trade ledger** *(Ch. 8, intraday)* — A table of completed trades with entry timestamp, exit timestamp, entry price, exit price, signed PnL, and any auxiliary diagnostic columns. The natural data structure for trade-level metrics: hit rate, expectancy, profit factor, per-trade Sharpe with bootstrap CI. Compare a *PnL series* (continuous bar-by-bar PnL) — different aggregation, different bootstrapping conventions.

**Trailing-window estimator** *(Ch. 10 §2, intraday)* — Any statistic (mean, std, quantile, regression coefficient) computed from the prior *L* observations, recomputed at each step. The natural point-in-time-clean replacement for whole-sample estimators in a backtest. On Ch10's strategy, replacing whole-sample σ with trailing-20-session σ moved the in-sample Sharpe from +0.82 to +1.64 — the bias direction is data-dependent, but the procedural fix (use a trailing window) is non-negotiable.

## U

**U-shape** *(Ch. 6, intraday)* — Intraday pattern where mean absolute return is high at the open, low at midday, and elevated (sometimes high, sometimes mild) into the close. The canonical *intraday seasonality* finding. On QQQ over a recent one-year window the open peak runs ~2.3× midday vol while the closing tail is much milder (~1.2×) — modern fragmented markets blunt the textbook closing peak.

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

**Vectorized backtest** *(Ch. 8, intraday)* — A backtest that computes PnL as a series of `signal × forward_return` products in one shot, without an explicit bar-by-bar loop. Fast to write and read, easy to vectorize with NumPy, but routinely violates point-in-time discipline. On Ch8's QQQ closing-window mean-reversion strategy, the same-bar bug roughly *doubles* the headline Sharpe (Ch9 §3 measured +1.57 same-close vs +0.80 next-open on the same data). Useful as a cheap sanity-check; **never** the production version. Compare *event-driven backtest* (Ch9).

**Volume bar** *(Ch. 6 §3, named only)* — A bar that closes whenever a fixed share-count of trading has occurred. Equalizes information density by share count. Compare *time bar*, *dollar bar*, *imbalance bar*.

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

---

## Ch. 14 additions — Position sizing and risk of ruin

The chapter's Key Terms table is the source of truth; entries below are reproduced verbatim from `14-position-sizing/README.md`. Appended here (rather than re-sorted alphabetically) per the project's "do not re-order existing glossary entries" convention.

**Bet size** *(Ch. 14)* — The fraction of equity (or fixed dollar amount) committed to a single trade. Distinct from leverage, which aggregates across positions.

**Leverage** *(Ch. 14)* — Ratio of total exposed notional to equity. A leverage multiplier of 5× means $5 of position per $1 of equity.

**Kelly criterion** *(Ch. 14)* — Bet-sizing rule that maximizes long-run expected log-wealth growth. Two forms: Bernoulli f\* = (bp − q)/b and continuous f\* = μ/σ².

**Full Kelly** *(Ch. 14)* — The Kelly-optimal fraction itself (k = 1). Theoretically growth-maximizing; in practice over-levered due to μ-estimation noise and Taylor-expansion breakdown on bp-scale returns.

**Fractional Kelly** *(Ch. 14)* — A scaled-down Kelly bet (k·f\* for k ∈ (0, 1)). Trades expected growth for reduced drawdown variance. Quarter-Kelly is a common practitioner ceiling.

**Fixed-fractional sizing** *(Ch. 14)* — Bet a fixed fraction of equity per trade, sized by stop distance: size = (r<sub>per_trade</sub> · equity) / d. Ignores μ; bets equal risk.

**Volatility targeting** *(Ch. 14)* — Set leverage so per-period PnL has a stated σ target: size = (τ<sub>daily</sub> · equity) / σ̂<sub>t</sub>. The chapter's recommended baseline.

**Drawdown stop** *(Ch. 14)* — A rule that reduces or halts position sizing when running drawdown from peak exceeds a threshold (e.g., halve-on-5%, halt-on-10%). A regime-change detector, not a growth tool.

**Risk of ruin** *(Ch. 14)* — Probability of breaching a terminal-loss threshold (e.g., 50% drawdown, account bust) over a stated horizon. Estimated by MC; extrapolated to deep tails by EVT.

**Expected log-wealth growth rate** *(Ch. 14)* — g = E[log(W<sub>t+1</sub>/W<sub>t</sub>)]. The objective Kelly maximizes; the right objective for a strategy compounding its own capital.

**f·σ diagnostic** *(Ch. 14)* — Per-trade equity-at-risk per σ of return. When f·σ is not ≪ 1, Kelly's Taylor expansion has broken down and the textbook formula is informational only.

**GPD shape ξ** *(Ch. 14)* — Tail-domain indicator from a Generalized Pareto fit. ξ < 0 bounded (Weibull), ξ = 0 exponential (Gumbel), ξ > 0 heavy (Fréchet / Pareto). The headline EVT parameter.

**DGP (data-generating process)** *(Ch. 14)* — The joint distribution producing each trade's return — μ, σ, tail shape, autocorrelation structure. Sizing rules in this chapter assume a stationary DGP; Ch15 / Ch16 relax that.

---

## Ch. 15 additions — Intraday vol and regime detection

The chapter's Key Terms table is the source of truth; entries below are reproduced verbatim from `15-intraday-vol-regime/README.md`. Appended here (rather than re-sorted alphabetically) per the project's "do not re-order existing glossary entries" convention.

**Volatility seasonality** *(Ch. 15)* — Systematic intraday pattern in σ (e.g., the open-midday-close U-shape on US equities). Estimated here as a trailing-60-session per-minute std with point-in-time discipline.

**EWMA** *(Ch. 15)* — Exponentially-weighted moving average of squared returns. Recursion σ̂²<sub>t</sub> = (1 − λ)·r²<sub>t−1</sub> + λ·σ̂²<sub>t−1</sub>; RiskMetrics default λ = 0.94. No long-run mean — drifts unboundedly if `r` runs hot.

**GARCH(1,1)** *(Ch. 15)* — The canonical vol-clustering model: σ²<sub>t</sub> = ω + α·r²<sub>t−1</sub> + β·σ²<sub>t−1</sub>, fit by MLE. Adds a long-run anchor ω that EWMA lacks.

**Persistence** *(Ch. 15)* — α + β in GARCH(1,1). Vol-shock half-life. Equity indices typically run 0.90-0.99 on long windows; on a 251-session sample this chapter measures 0.84, near the lower bound of identifiability.

**Long-run variance** *(Ch. 15)* — ω / (1 − α − β) in a stationary GARCH(1,1). The unconditional variance the recursion drifts toward when no innovations arrive.

**Standardized residual** *(Ch. 15)* — z<sub>t</sub> = r<sub>t</sub> / σ̂<sub>t</sub>. Should be ~N(0, 1) if σ̂<sub>t</sub> is correctly specified. ACF(z²) ≈ 0 is the GARCH-fit diagnostic.

**Regime** *(Ch. 15)* — A stretch of time during which the DGP's parameters are stable. A regime change is a parameter shift (most often in σ²). Regimes are latent — only estimated, never directly observed.

**Hidden Markov model (HMM)** *(Ch. 15)* — A two-layer model: latent discrete state s<sub>t</sub> evolving as a Markov chain, observation r<sub>t</sub> drawn from a state-specific emission. Fit by EM; the 2-state Gaussian variant in §5.3 is the canonical regime-detection workhorse.

**EM algorithm** *(Ch. 15)* — Iterative MLE procedure for latent-variable models. E-step: compute posterior over latent states given current parameters (forward-backward for HMMs). M-step: maximize expected complete-data log-likelihood. Iterate until convergence; doesn't guarantee a global optimum.

**CUSUM change-point** *(Ch. 15)* — Cumulative-sum statistic on a mean-zero residual (here, z² − 1). Flags the session at which a persistent drift reaches a √t-scaled threshold. Sensitivity tuned by the multiplier k; canonical k = 5 needs hundreds of thousands of obs to fire.

---

## Ch. 16 additions — More strategies: momentum, breakout, event-driven

The chapter's Key Terms table is the source of truth; entries below are reproduced verbatim from `16-more-strategies/README.md`. Appended here (rather than re-sorted alphabetically) per the project's "do not re-order existing glossary entries" convention.

**Momentum** *(Ch. 16)* — A strategy family that bets on continuation of the most recent move. Operationally: enter when the trailing-N return exceeds a vol-scaled threshold; hold K minutes. Ch7 §6's positive lag-120 ρ is the hint this chapter pursues.

**Opening range (OR)** *(Ch. 16)* — The price interval [min L, max H] traversed during the first 30 minutes of the RTH session. The reference range whose break the ORB family trades. Mean width on QQQ on this window: 50.5 bp; p75: 72.2 bp.

**Breakout confirmation** *(Ch. 16)* — An ORB execution variant that enters at the *close* of the breaking bar with a market order. Takes liquidity; pays the spread on entry; fill certainty ≈ 1. The variant whose OR-p75 × ε=10 cell is the chapter's single positive cost-aware result.

**Breakout anticipation** *(Ch. 16)* — An ORB execution variant that posts a stop-limit at OR<sub>high</sub> + ε bp (long) or OR<sub>low</sub> − ε bp (short) before the break confirms. Makes liquidity; earns the spread when filled; subject to Ch13 toxicity. On this data toxicity (+1.82 bp) exceeds the rebate (~0.72 bp).

**False break** *(Ch. 16)* — A bar that crosses the OR boundary intra-bar but closes back inside. The wick is microstructure noise, not directional information. Filtered by requiring close-based triggers and ε > 0 padding.

**Event-driven strategy** *(Ch. 16)* — A family that trades around scheduled releases (FOMC, CPI, NFP) on the assumption that pre-release positioning or post-release information propagation creates predictable short-window drift. Pain point on a single-symbol single-year window: sample size.

**Pre-release drift (H1)** *(Ch. 16)* — The event-driven hypothesis that sign(pre-window return) predicts sign(release-window return). Mechanism: positioning flow ahead of a known event leaves a directional residue. Bootstrap CI on QQQ FOMC N=8: (−41.6, +2.1) — no verdict.

**Post-release continuation (H2)** *(Ch. 16)* — The event-driven hypothesis that sign(release-window return) predicts sign(post-window return). Mechanism: information propagation continues the initial move. Bootstrap CI on QQQ FOMC N=8: (−25.7, +7.1) — no verdict.

**Regime fingerprint** *(Ch. 16)* — The family × regime Sharpe heatmap. Reads "where does this family work?" rather than "is this family good on average?". Useful for combination logic (Exercise 4); fragile to per-cell N.

**Family-dependent execution** *(Ch. 16)* — The rule that the right order type depends on the family's expected post-signal move direction. MR makes (move reverses to fill); momentum and breakout-confirmation take (move is in progress); breakout-anticipation makes and gets toxified (resting limit fills when break fails). Derived from Ch13 §3-§4.
