# Chapter 7 — Linear Regression Primer

> Six chapters used regression-flavored ideas without ever doing a regression: Ch3 had β̂ in scatter plots; Ch4 used "regress on X" as one of four μ-flavors; Ch5 had SE-of-mean; Ch6 had Σ⁻¹ — the same matrix shape as the closed-form OLS solution. Chapter 7 collects all of it into the one piece of inferential statistics the rest of the curriculum cannot live without.

The chapter has **one running example** — XLK regressed on SPY over the same 20-year window as Chapters 3–6 — and **three jobs** you can do with a regression. The reader meets all three on the same XLK-on-SPY line, which Chapter 8 then picks up as **CAPM**.

### Reader takeaway

A regression has *three jobs* — describe the relationship, decide whether the relationship is real (inference), and use it to predict. They are different jobs, with different error bars and different failure modes. *Always know which job you are doing.*

### Learning objectives

After this chapter you can:

1. Read a regression coefficient as **"a one-unit change in *x* is associated with a β̂-unit change in *y*, on average."**
2. Read a t-statistic and p-value, and translate them into "is this slope statistically distinguishable from zero?"
3. Read R² as "the in-sample fraction of variance in *y* that *x* explains" — and know what it does *not* mean.
4. Plot residuals vs fitted and recognise the three classic pathologies (non-linearity, heteroskedasticity, autocorrelation).
5. List the top three pitfalls that wreck regression-based inference: **omitted-variable bias, look-ahead bias, spurious correlation.**
6. Run an OLS in `statsmodels` and read every line of its summary table.

## What we mean by "doing a regression"

| Flavor | Question it answers | Key statistic | Section |
|---|---|---|---|
| **Description** | What is the average relationship between *x* and *y* in this data? | β̂ (slope), α̂ (intercept), R² | §2 |
| **Inference** | Is the relationship statistically distinguishable from zero? | SE(β̂), t-statistic, p-value, 95% CI | §3 |
| **Prediction** | What value of *y* should I expect for a new *x*, with what uncertainty? | ŷ, prediction interval | §4 |

The flavors are *mostly additive* — inference uses the descriptive fit; prediction uses both. Knowing which flavor you're doing tells you which error bar to trust and which pitfall to guard against. The three flavors all rest on the same SE formulas; §5 audits whether those SEs are trustworthy.

## 1. Setup

Same 8-ticker basket as Ch3–6 (running example uses **SPY** and **XLK**; **TLT** joins in §6/§7). Daily log returns over the 20-year window — N ≈ 5,030 observations from May 2006 to May 2026. One new library:

> **`statsmodels`** — Python's standard regression library. Wraps the same NumPy linear-algebra you'd write by hand, but produces the full inference output (standard errors, t-statistics, p-values, confidence intervals) automatically. Convention: `import statsmodels.api as sm`.

The notebook adds `statsmodels>=0.14` to `requirements.txt`. No new data sources.

## 2. OLS by example — description

Pick **SPY** on the x-axis (broad market) and **XLK** on the y-axis (tech sector). Both daily log returns. Roughly 5,030 paired observations.

The regression line answers: *on a day SPY is up 1%, what does XLK do on average?*

### 2.1 Least squares — the math in one screen

Pick (α, β) to minimise the sum of squared residuals:

> SS(α, β) = Σ<sub>t</sub> (y<sub>t</sub> − α − β·x<sub>t</sub>)²

where:
- *y<sub>t</sub>* — XLK's log return on day *t*. **Units:** decimal log return.
- *x<sub>t</sub>* — SPY's log return on day *t*. Same units.
- *α* (intercept) — average y when x = 0. Same units as y.
- *β* (slope) — change in y per unit change in x. Dimensionless.

Setting the partial derivatives to zero gives the closed forms:

> β̂ = Cov(x, y) / Var(x)
>
> α̂ = ȳ − β̂·x̄

The **residual** is what's left after the fit: ε̂<sub>t</sub> = y<sub>t</sub> − α̂ − β̂·x<sub>t</sub>. The **fitted value** is what the line predicts: ŷ<sub>t</sub> = α̂ + β̂·x<sub>t</sub>.

<details><summary>Brief derivation of β̂</summary>

Take ∂SS/∂α = 0 and ∂SS/∂β = 0:

> ∂SS/∂α = −2 Σ (y<sub>t</sub> − α − β·x<sub>t</sub>) = 0 ⟹ α̂ = ȳ − β̂·x̄
>
> ∂SS/∂β = −2 Σ x<sub>t</sub>·(y<sub>t</sub> − α − β·x<sub>t</sub>) = 0

Substituting α̂ into the second equation and solving for β̂ gives β̂ = Σ(x − x̄)(y − ȳ) / Σ(x − x̄)² = Cov(x, y) / Var(x).

</details>

### 2.2 The fit on XLK and SPY

Running `sm.OLS(y, sm.add_constant(x)).fit()` on the 20-year panel produces:

| Quantity | Value |
|---|---|
| β̂(SPY) | **1.0795** |
| α̂ (daily) | +0.000148 |
| α̂ × 252 (annualized) | **+3.72%** |
| 95% CI on annualized α̂ | (−0.34%, +7.77%) — *just barely straddles zero* |
| t(α̂) | 1.80 (p = 0.073) |
| R² | **0.838** |
| N | 5,030 daily observations |

**Reading the picture.** β̂ ≈ 1.08 means *on a day SPY is up 1%, XLK is up about 1.08% on average.* α̂ near zero on a daily basis (+3.7% annualized) means *controlling for SPY, XLK has a small positive average drift left over.* R² ≈ 0.84 means *about 84% of XLK's daily-return variance is explained by SPY's.*

Three caveats sit immediately under that picture:
1. β̂ is an *average* — individual days vary a lot. The dispersion is the residual.
2. R² ≈ 0.84 is high *for a regression of one asset on another*; it is not high in absolute terms — about a sixth of XLK's variance is *not* SPY-explained, and that sixth is exactly where stockpicking lives.
3. The annualized α of 3.7% sounds meaningful — but is it *statistically* distinguishable from zero? §3 quantifies the error bars.

### 2.3 What the scatter plot shows

The scatter of (SPY, XLK) daily log returns is a roughly elliptical cloud tilted up-and-right; the fitted line cuts through its long axis with slope ≈ 1.08. The cloud is densest near (0, 0) — most days are small moves — and stretches into both tails. The widest residuals — the points that escape the cloud — concentrate in 2008-09 (Lehman / global financial crisis), March 2020 (COVID drawdown), and Q4 2022 (rate-shock selloff). Those are the days SPY's slope misses XLK's move by the most. The widening near the extremes is the *heteroskedasticity* — variance that depends on x; defined in §5 — which §5 will diagnose formally.

## 3. Inference — is the relationship real?

§2 said β̂ ≈ 1.08 and annualized α̂ ≈ 3.7%. Inference asks *are those numbers statistically distinguishable from zero?* The answer rides on the standard errors.

### 3.1 Standard error, t-statistic, confidence interval

Same machinery as Ch5's SE-of-mean, applied to a slope:

> SE(β̂) = σ̂<sub>ε</sub> / √( Σ<sub>t</sub> (x<sub>t</sub> − x̄)² )

where:
- *σ̂<sub>ε</sub>* — sample standard deviation of the residuals. **Units:** decimal log return.
- *x<sub>t</sub>*, *x̄* — SPY's daily log return at *t* and its sample mean. Same units.
- *SE(β̂)* — the standard error of the slope. Dimensionless.

The shape mirrors Ch5's SE(μ̂) = σ/√N: more data and more spread in *x* both make the slope estimate sharper. *Intuition: a wide x-range gives the line a long lever arm — small wobbles in the cloud rotate the line less. A narrow x-range and the slope can swing wildly between fits.*

The **t-statistic** under H₀ (the *null hypothesis* — the conservative claim that the slope is zero, i.e. β = β₀) is:

> t = (β̂ − β₀) / SE(β̂)

For our N ≈ 5,030 (5,028 degrees of freedom), the t-distribution is indistinguishable from standard-normal. The **95% confidence interval** is β̂ ± 1.96·SE(β̂). The **p-value** is the probability of seeing |t| this large or larger under H₀. Ch4 introduced the t-statistic on the sample mean of returns; here it's the same construction on a regression coefficient — the only change is what's in the numerator and denominator.

### 3.2 Reading the statsmodels coefficients block

The notebook's `summary()` output has a coefficients block with six columns. Walking each one:

- **coef** — point estimate. β̂ = 1.0795; α̂ = +0.000148 daily.
- **std err** — SE of the coefficient. SE(β̂) = 0.0067 is tiny relative to β̂ ≈ 1.08 — both because N ≈ 5,030 is large (the √N in the SE denominator shrinks the SE) and because SPY's daily-return spread is wide (the Σ(x − x̄)² term in the denominator is large). SE(α̂) = 8.21 × 10<sup>−5</sup> is about half the size of α̂ itself — which is why the t-stat is only 1.80.
- **t** — coef / std err. **161 for β** (overwhelming); **1.80 for α** (borderline).
- **P>|t|** — two-sided p-value for H₀: coefficient = 0. **0.000 for β; 0.073 for α** (does not reject at 95%).
- **[0.025, 0.975]** — the 95% CI. (1.066, 1.093) for β — excludes zero by a country mile. (−0.0034, +0.0777) annualized for α — *just barely straddles zero*.

<details><summary>Reading the summary footer (Durbin-Watson, Jarque-Bera, Omnibus, Skew, Kurtosis, Cond. No.)</summary>

The block at the bottom of `summary()` is a quick assumption-audit — the same diagnostics §5 plots, in scalar form:

- **Durbin-Watson** — test for lag-1 autocorrelation in the residuals. ≈ 2.0 means none; <1.5 or >2.5 is a flag. Ours is 2.10 — clean at the level.
- **Jarque-Bera (JB)** — joint test for skew and excess kurtosis in residuals vs Normal. Big number = non-Normal residuals; we get JB = 3,514, p ≈ 0 — the fat-tail finding §5.2 confirms.
- **Omnibus** — another Normality test on the residuals; same flavor as JB. Big = non-Normal.
- **Skew** — sample skewness of the residuals. Normal = 0; ours = −0.14, mildly left-skewed.
- **Kurtosis** — sample kurtosis of the residuals. Normal = 3; ours = 7.1 — fat tails.
- **Cond. No.** — condition number of the design matrix; multicollinearity warning. Single regressor here, so it's small (81.6); large numbers (>30 with multiple regressors) flag collinearity (§7).

</details>

### 3.3 Two natural tests

**Is β = 0?** No — t ≈ 161, p ≈ 0. XLK's daily return is overwhelmingly explained by SPY's. *Boring* — anyone watching tech and the broad market knows this.

**Is α = 0?** This is the *interesting* test. Annualized α̂ ≈ +3.72% with 95% CI (−0.34%, +7.77%) and t = 1.80, p = 0.073. **The CI just barely includes zero.** XLK's apparent outperformance is *not* statistically distinguishable from zero at the conventional 95% level, even with 20 years of daily data. *With another 2-3 years of similar daily data — assuming α̂ stays near +0.000148 — the SE shrinks enough that the lower CI bound crosses zero.*

This is the sceptical foundation for Ch8's CAPM-α discussion: even on assets that *look* like they outperformed, two decades of evidence often produce statistically borderline cases.

> **Foot-gun: textbook SEs assume i.i.d. Gaussian residuals.** *i.i.d. — independent and identically distributed — every observation drawn the same way, with no carryover from past values.* Daily-equity residuals are neither (vol clustering — Ch2; fat tails — Ch2 and Ch10). Textbook p-values are therefore *slightly* optimistic; true confidence intervals are *slightly* wider. §5 exposes the violations diagnostically. Full robust treatment uses **HAC / Newey-West** standard errors — *HAC = heteroskedasticity-and-autocorrelation-consistent SEs; corrects exactly the §5 violations* (`cov_type='HAC'` in statsmodels). Named only here.

## 4. Prediction and R²

§4 separates two things readers often conflate: **R²** (an in-sample descriptive number) and **prediction** (claiming the line will hold on new data, with its own error bar).

### 4.1 R² formally

> R² = 1 − SS<sub>res</sub> / SS<sub>tot</sub>

where:
- *SS<sub>res</sub>* = Σ (y<sub>t</sub> − ŷ<sub>t</sub>)² — residual sum of squares.
- *SS<sub>tot</sub>* = Σ (y<sub>t</sub> − ȳ)² — total sum of squares.
- *R²* — in-sample fraction of variance explained. Range [0, 1] (with intercept). In simple regression, equals corr(x, y)².

**Adjusted R²** penalises for added regressors:

> R²<sub>adj</sub> = 1 − (1 − R²) · (n − 1) / (n − k − 1)

where:
- *n* — number of observations.
- *k* — number of regressors not counting the intercept.

For k = 1, adjusted and raw R² are nearly identical; the gap matters in §7.

### 4.2 What R² is *not*

R² is the **in-sample** fraction of variance explained by the fit on *this* data. It is *not* the fraction the model will explain on new data. Out-of-sample R² is typically lower; on poor models it can go negative — worse than predicting the mean.

A model can have R² = 0.95 in-sample and R² = 0 (or negative) on next month's data. **R² alone tells you nothing about predictive ability.** Out-of-sample testing is **Chapter 13.**

### 4.3 Prediction interval

For a new x, the model predicts ŷ = α̂ + β̂·x. Two error bars matter, with very different widths:

> **CI on the regression line:** ŷ ± 1.96 · SE_line(x)
>
> **Prediction interval:** ŷ ± 1.96 · √( σ̂²<sub>ε</sub> + SE_line(x)² )

where:
- *SE_line(x)* — uncertainty in *where the line is* at this particular x. Comes from uncertainty in α̂ and β̂.
- *σ̂²<sub>ε</sub>* — residual variance. The irreducible day-to-day scatter around the line.
- *Prediction interval* — error bar on a *new individual observation*, not on the line.

The CI on the line is narrow (line-fitting is precise with N ≈ 5,030). The prediction interval is much wider because it includes the residual scatter on top.

For a +1% SPY day:

| Quantity | Value |
|---|---|
| ŷ (predicted XLK return) | ≈ +1.09% |
| 95% CI on the line | tight — order of ±0.02% |
| 95% prediction interval | wide — order of ±1.14% |

The line is precise; predicting *next Monday* is not — anywhere from −0.05% to +2.24% would be unsurprising under the model on a +1% SPY day.

## 5. Residual diagnostics — three plots that audit the SEs

§3's standard errors assume residuals are independent and normally distributed. Three plots check whether that assumption holds; each pathology has a name and a fix.

### 5.1 Residuals vs fitted values

**What you want:** flat horizontal cloud around zero, constant width.

**Three pathologies:**

- *Curvature* — the relationship isn't linear after all (the cloud bends).
- *Fan shape* — heteroskedasticity. Residual variance grows with x; SEs are typically too small under heteroskedasticity (the OLS formula assumes constant variance), so t-stats are inflated and CIs too narrow. Use robust SEs (statsmodels `cov_type='HC3'`) to fix.
- *Clusters* — an omitted nonlinear effect or a regime structure.

The SPY/XLK residuals are roughly flat-cloud, with a noticeable widening near the extremes — the widest residuals are 2008-09 (GFC), March 2020 (COVID), and 2022 (rate-shock selloff) — the same vol windows Ch2 named — the fat-tail signature §5.2 confirms.

### 5.2 Q-Q plot of residuals against Normal

**What you want:** the points sit on the diagonal.

**Pathology:** the points peel away at the ends — the residual distribution has fatter tails than the Normal it's being compared to.

Daily-equity residuals *will* show fat-tail departure; this is Ch2's lesson restated. The *kurtosis (Ch2) — a fat-tail score; Normal sits at 3.0, daily equities sit around 7* — of these residuals is ≈7.1, vs Normal's 3.0 — almost identical to Ch2's headline equity-return kurtosis, transferred to the regression scale. Textbook p-values are therefore *slightly* optimistic; true CIs are *slightly* wider. The proper fix is **Extreme Value Theory** on residuals — Ch10. For now: report the p-values, but don't treat a t = 2.05 like a discovery.

### 5.3 Residual ACF and squared-residual ACF

The notebook plots two autocorrelation functions side-by-side.

**Residual ACF:** flat near zero across lags. The lag-1 ACF is −0.05 — barely above noise; the i.i.d. assumption *mostly* survives at the level of residuals themselves.

**Squared-residual ACF:** *not* flat. Lag-1 ACF is +0.21; lag-2 +0.26; slow positive decay across many lags. This is **vol clustering** showing up cleanly — today's *i.i.d.* (independent and identically distributed) assumption fails because today's |residual| predicts tomorrow's |residual|.

That's the Ch9 GARCH preview — *GARCH = generalized autoregressive conditional heteroskedasticity, the standard model for vol clustering; Ch9*. The fix for time-correlated residual *variance* is GARCH; the fix for any time-correlated residuals at the *level* is HAC SEs (`cov_type='HAC'`, named only here).

## 6. Pitfalls — the three ways regression fools you

Three classic failure modes. Each gets one paragraph and one numerical illustration.

### 6.1 Omitted-variable bias (OVB)

When a regression leaves out a variable that (a) explains *y* and (b) correlates with the included regressor, the included coefficient absorbs some of the omitted variable's effect.

The §7 multi-regression is the same fit, repurposed. Refitting XLK on **SPY + TLT** instead of SPY alone moves SPY's coefficient by about −0.012 (1.0795 → 1.0918) — small, because SPY and TLT have low correlation over this window. **TLT's own coefficient is +0.052 with t ≈ 5.7** — small but statistically distinguishable. The SPY-only regression hid a genuine (mild positive) bond loading inside ε. The principle is general: every omitted regressor that correlates with an included one biases the included coefficient.

<details><summary>Closed-form OVB</summary>

If the true model is *y = α + β₁ x₁ + β₂ x₂ + ε* and you fit *y = α + γ x₁ + ν*, then E[γ̂] = β₁ + β₂ · Cov(x₁, x₂) / Var(x₁). The bias is the slope of x₂ on x₁ times the omitted coefficient.

where:
- *γ̂* — the slope you actually estimate when you (wrongly) fit y on x₁ alone.
- *β₁* — the true slope on x₁ in the correct model.
- *β₂* — the true slope on the omitted regressor x₂.
- *x₁* — the regressor you included.
- *x₂* — the regressor you omitted.

</details>

### 6.2 Look-ahead bias

Regressing today's return on tomorrow's information looks predictive — and isn't. Easy to introduce accidentally: rolling z-scores computed with future data, target-leakage in feature engineering, label-aligned-wrong rolling joins.

The fix is procedural: every feature available at time *t* must be available *strictly before t*. Concept revisited rigorously in **Ch13** backtesting.

### 6.3 Spurious correlation

Two random walks with no causal connection can produce a regression with massive |t| (and on different seeds, sometimes also impressive R²). The numbers look real because the walks share *trend*, not because either drives the other. This is the **spurious-regression** problem.

The empirical fix is to regress on *changes* (returns), not *levels* (prices). When the levels really do co-move, the proper response is **cointegration** analysis — named only here. **Exercise 4** makes the point quantitatively — across 100 trials, the conventional |t| > 2 bar is cleared in roughly 90+% of cases on pure-noise random walks.

## 7. Multiple regression briefly

Two regressors instead of one. The math is exactly Ch6's Σ⁻¹ shape.

### 7.1 The math

> y = α + β₁·x₁ + β₂·x₂ + ε

In matrix form: **y = Xβ + ε** with X = [**1** | **x**₁ | **x**₂]. The closed form is:

> β̂ = (XᵀX)⁻¹ Xᵀ y

where:
- *X* — n × (k + 1) design matrix; first column all 1s for the intercept; remaining k columns the regressors.
- *β̂* — (k + 1) × 1 column of estimated coefficients (intercept first).
- *(XᵀX)⁻¹* — same matrix-inverse shape as Ch6's **Σ⁻¹**. Same instability when columns of X are highly correlated.

That instability is **multicollinearity** — when two regressors carry nearly the same information, their individual coefficients become unstable (huge SEs) even though the overall fit is fine. *Imagine SPY and a SPY-clone with corr 0.999 — both coefs swing wildly between fits while their sum β₁ + β₂ stays stable.* One-paragraph gloss only; named extensions — *variance inflation factors* (per-regressor collinearity scores) and *partial regression plots* (residual-on-residual scatter) — are out of scope.

### 7.2 XLK on SPY + TLT

Refitting XLK on SPY + TLT:

| Quantity | SPY only | SPY + TLT |
|---|---|---|
| β̂(SPY) | 1.0795 | 1.0918 (barely moves) |
| β̂(TLT) | — | **+0.0522 (t = 5.7)** |
| α̂ (daily) | +0.000147 | +0.000135 |
| R² | 0.838 | 0.839 (tiny uptick) |

SPY's coefficient moves modestly; TLT's coefficient is small but t-distinguishable. **TLT carries additional information about XLK's daily moves beyond what SPY captures, but only a tiny amount** — the Δ R² is 0.001. The "right" answer to the question *what determines XLK's daily return* requires more than just SPY, but adding regressors hits diminishing returns fast.

**Why we stop here.** Replacing TLT with size and value factors is **CAPM with Fama-French**, which is **Chapter 8.** This chapter has now built every piece of inferential machinery Ch8 needs.

## 8. What we just learned — three flavors, three diagnostics, three pitfalls

- **Description** (β̂, α̂, R²) — the average relationship in this data. Easy to compute, easy to over-interpret.
- **Inference** (SE, t, CI, p) — is the relationship statistically distinguishable from zero? Critical in finance: most things look related at the point estimate; few survive a CI audit. (XLK's apparent 3.7% annualized α has p = 0.073 — borderline.)
- **Prediction** (ŷ, prediction interval) — what to expect for a new x, with much wider error bars than the line CI.
- **Diagnostics** (residuals vs fitted, Q-Q, ACF) — three plots that audit whether the SEs you just trusted should actually be trusted.
- **Pitfalls** (OVB, look-ahead, spurious) — avoid these and a regression is a tool; ignore them and a regression is how to fool yourself with statistics.

## 9. So what?

**Decision rules:**

- **Always look at the residual plots** before trusting the SEs. A regression you haven't diagnosed is a regression you don't trust.
- **t > 2 is the conventional bar — but a low one.** A single t = 2.1 in a 5,030-sample fit is p ≈ 0.04, well within the tested-many-things zone — *if you ran 20 regressions looking for a result, one of them would clear t > 2 by pure chance, so a lone t = 2.1 isn't evidence of much.* **Exercise 4** is the random-walk drill that demonstrates how easy this bar is to clear by chance on non-stationary series.
- **R² is not a quality score.** R² ≈ 0.84 between XLK and SPY says they move together, not that the fit is "good." Out-of-sample is Ch13.
- **Add a regressor when you suspect OVB; remove when collinearity blows up SEs.** §7's TLT addition is the OVB-add example.

**What this chapter can't yet tell you:**

- Whether the relationship is *causal*. OLS is correlational. Causal identification — *instrumental variables* (use a third variable that affects x but not y directly); *RDD — regression discontinuity* (compare just-above vs just-below a cutoff); *DID — difference-in-differences* (treated-vs-control across a policy change) — is out of scope.
- Whether the relationship survives **out of sample**. **Ch13.**
- How to combine many correlated regressors with *shrinkage — pulling coefficients toward zero to reduce overfit; ridge and lasso are two flavors* (ridge shrinks all toward zero, lasso shrinks some to exactly zero). Out of scope; **Ch8** Fama-French is the closest in-scope case.
- How to handle classification problems. **Future Ch12.**

## 10. Up next

**Chapter 8 — Factor Models: CAPM and Fama-French.** Ch8 is two regressions back-to-back. CAPM is one regression of (asset return − r<sub>f</sub>) on (market return − r<sub>f</sub>); the slope is the famous **β** and the intercept is **α**. Fama-French is the same with size and value as additional regressors. Everything you just learned — the descriptive fit, the inference machinery, the residual diagnostics, the OVB pitfall — is the toolkit. Ch8 also pays Ch3 §3.5's "hidden factor exposure" promise: the 8-asset basket isn't as diversified as it looks once you regress it on the market.

## Key Terms

| Term | Definition |
|---|---|
| **Ordinary least squares (OLS)** | The procedure that picks (α, β) to minimise the sum of squared residuals. |
| **Residual** | Observed minus fitted value, ε̂<sub>t</sub> = y<sub>t</sub> − ŷ<sub>t</sub>. |
| **Fitted value** | The model's prediction at an observed x, ŷ<sub>t</sub> = α̂ + β̂·x<sub>t</sub>. |
| **Slope (β̂)** | Change in y per unit change in x, on average. |
| **Intercept (α̂)** | Average y when x = 0. |
| **Standard error of a coefficient** | Standard deviation of the coefficient's sampling distribution. |
| **t-statistic** | (Coefficient − null value) / SE. Approximately standard-normal under H₀ for large N. |
| **p-value** | Probability of seeing \|t\| this large or larger under H₀. |
| **95% confidence interval** | β̂ ± 1.96·SE(β̂). The range of slope values consistent with the data at 95%. |
| **R² (coefficient of determination)** | In-sample fraction of variance in y explained by the regression. |
| **Adjusted R²** | R² penalised for added regressors. |
| **Prediction interval** | Error bar on a new ŷ, wider than the CI on the regression line because it includes residual scatter. |
| **Heteroskedasticity** | Residual variance that depends on x. Breaks textbook SE formulas. |
| **Autocorrelated residuals** | Residuals where ε̂<sub>t</sub> predicts ε̂<sub>t+1</sub>. Breaks the i.i.d. SE assumption. |
| **Omitted-variable bias (OVB)** | Bias in an included coefficient from leaving out a correlated regressor that also explains y. |
| **Multicollinearity** | Two regressors carrying near-identical information; produces unstable individual coefficients. |
| **Look-ahead bias** | Using future information to predict the present. Inflates apparent fit. |
| **Spurious correlation** | Apparent regression relationship between unrelated series, often via shared trend. |
| **`statsmodels`** (named) | Python library providing OLS with full inference output (SEs, t-stats, p-values, CIs). |
| **i.i.d.** | Independent and identically distributed — every observation drawn the same way, with no carryover from past values. Standard textbook assumption for SE formulas. |
| **Kurtosis** (Ch2) | A fat-tail score for a distribution; Normal sits at 3.0, daily equities sit around 7.0. Higher = more weight in the tails. |
| **HAC / Newey-West SEs** | Heteroskedasticity-and-autocorrelation-consistent standard errors; corrects exactly the §5 violations (`cov_type='HAC'`). Named only here; Ch9 revisits. |
| **GARCH** | Generalized autoregressive conditional heteroskedasticity — the standard model for vol clustering; Ch9. |
| **Variance inflation factor (VIF)** | Per-regressor collinearity score; large values (>10) flag multicollinearity. Out of scope. |
| **Shrinkage (ridge, lasso)** | Pulling regression coefficients toward zero to reduce overfit; ridge shrinks all toward zero, lasso shrinks some to exactly zero. Out of scope. |
| **RDD (regression discontinuity)** | Causal-inference design that compares observations just above and just below a cutoff. Out of scope. |
| **DID (difference-in-differences)** | Causal-inference design that compares treated and control groups across a policy change. Out of scope. |

## Exercises

Try these in fresh cells in the companion notebook. Solutions are not provided — the goal is to consolidate the chapter's machinery on slightly different inputs.

1. **Per-asset CAPM-style table.** For each of TLT, GLD, XLF, XLE, XLV, XLU, regress its daily log return on SPY's. Tabulate β̂, α̂ (annualized), t(α̂), t(β̂), R². Test the *daily* α̂ for ≠ 0 (that is the t-stat statsmodels prints); report annualized α̂ only as the headline point estimate. Which sectors have R² above 0.80? Which have α̂ statistically distinguishable from zero at 95%?

2. **OVB illustration.** Regress XLE on SPY only, then on SPY + GLD. How much does XLE's SPY coefficient change? What does the SPY-only regression's residual contain that the multi-regressor fit pulls out into a separate β? *(Hint: XLE has commodity-and-dollar exposure not captured by SPY.)*

3. **Diagnose a residual.** Take any single-regressor fit from Exercise 1 and plot the three diagnostic plots from §5 (residuals vs fitted, Q-Q vs Normal, ACF of squared residuals). Which pathologies (fat tails, autocorrelation, heteroskedasticity) appear?

4. *(stretch)* **Spurious-correlation drill.** Generate two independent random walks of length N = 5,000. Regress one on the other. What R² do you get? What t-statistic on the slope? Repeat 100 times and plot the distribution of |t|. How often does |t| > 2 by pure chance?
