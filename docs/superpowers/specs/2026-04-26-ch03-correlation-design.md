# Chapter 3 — Multiple Assets: Correlation and Diversification

**Status:** Design approved 2026-04-26
**Author chapter slot:** `03-correlation/`
**Predecessor:** Chapter 2 — Risk: Volatility Clustering and Fat Tails (`02-risk/`)
**Successor (planned):** Chapter 4 — Risk metrics (drawdown, VaR, Sharpe)

---

## 1. Background and motivation

Chapters 1 and 2 lived inside a single asset. The reader can now reason about *one* return distribution — its mean, its volatility, its fat tails, its time-varying variance. That's enough to think about a single position, but not enough to think about a *portfolio*.

Chapter 2's "What we mean by risk" framing named **correlation risk** as the *entire subject of Chapter 3*. Chapter 3 cashes that promise. It introduces the statistical machinery for thinking about how assets move *together*, and — following the precedent set by Ch2 — pairs the textbook tools with empirical findings about how the textbook fails.

Two specific cross-chapter setups also pay off here:
- Ch2 §3.2 introduced **covariance** with the explicit forward pointer "will reappear as the central object of Chapter 3." It does. Cov is the building block of correlation, the diagonal of the covariance matrix is the variance vector from Ch2, and the off-diagonals carry everything new.
- Ch2's recap reframed risk as having multiple flavors. Ch3 takes one of those flavors (correlation risk) and recursively breaks *it* into sub-flavors.

## 2. Goals and non-goals

### Goals

- Open with a "What we mean by correlation risk" section that names sub-flavors and signals scope (concept-before-statistic per the saved feedback memory).
- Build the textbook tools: pairwise Pearson correlation, the correlation matrix as an object, two-asset and N-asset portfolio variance.
- Demonstrate the diversification math empirically: equal-weighted basket vol as N grows, the irreducible floor when assets share correlation, the cross-asset vs within-asset-class contrast.
- Show empirically that **correlations themselves aren't constant** (the Ch2 mirror): rolling correlation flipping signs across regimes, conditional correlation in stress vs calm, the calm-vs-crisis heatmap diptych.
- Translate every major statistical finding into dollar / lived-experience terms (the saved "concept before statistic" memory).
- Recap by concept-flavor, not by tool.

### Non-goals (explicitly deferred)

- **Markowitz mean-variance optimization** — efficient frontier, tangency portfolio, full quadratic programming. Natural fit for its own chapter once Ch3 establishes the building blocks.
- **Risk parity** — mentioned in passing as one of several weighting schemes; full treatment deferred.
- **Sharpe ratio, drawdown, VaR** — owed since Ch1; consolidated into Ch4 risk-metrics chapter.
- **Factor models (CAPM, Fama-French, PCA on returns)** — listed in the deferred-flavors section as "hidden factor exposure"; future chapter.
- **Tail dependence and copulas** — listed as deferred flavor; much later (alongside EVT).
- **Time-varying correlation models (DCC-GARCH)** — Ch3 demonstrates time-varying correlation empirically but does not formally model it. Same deferral pattern as Ch2's GARCH-as-named-but-deferred.

## 3. Narrative arc

Three-part structure with deliberate Ch2 mirror:

> Chapter 2 said: a single asset's distribution isn't normal (Part I) and isn't stationary (Part II). Chapter 3 says: a *pair* of assets has a co-movement number (Part I), a *portfolio* of assets aggregates those co-movements into total risk (Part II), and that aggregation isn't stationary either — correlations themselves shift across regimes, weakening diversification when it's needed most (Part III).

Order rationale: pairwise → aggregation → regime is the natural pedagogical staircase. Each step adds one new conceptual object: a single correlation number → a matrix of them → a time-series of matrices.

## 4. Data

- Eight tickers in one `yf.download(...)` call: **SPY, TLT, GLD, XLK, XLF, XLE, XLV, XLU**.
- 20-year window (`period="20y"`) — continuity with Ch2; covers 2008, 2020, 2022.
- Log returns throughout (continuity with Ch2).
- The eight tickers serve different storytelling roles:
  - **Cross-asset trio (SPY, TLT, GLD):** carries pairwise visuals and the regime-shift demo. TLT's correlation with SPY famously *flips sign* across regimes — the chapter's most dramatic finding.
  - **Sector ETFs (XLK, XLF, XLE, XLV, XLU):** carry the within-asset-class portfolio-math heatmap and the "diversification within equities is limited" lesson.
  - **All eight:** master correlation heatmap; the calm-vs-crisis diptych.

## 5. Section structure

### Concept-flavors framing (before §1)

A "**What we mean by correlation risk**" section, mirroring Ch2's "What we mean by 'risk'" pattern. Names five flavors, says which the chapter covers vs defers:

| Flavor | This chapter |
|---|---|
| Pairwise correlation | Part I |
| Aggregation / portfolio risk | Part II |
| Regime / crisis correlation | Part III |
| Hidden factor exposure | Deferred — future factor-models chapter |
| Tail dependence | Deferred — much later (with EVT / copulas) |

When the chapter says "correlation risk" later, it means *the magnitude, aggregation, and regime dimensions* — not "everything anyone has ever called correlation risk." Same disclaimer pattern as Ch2.

### §1. Setup and data refresh

- Imports identical to Ch2 (no new dependencies).
- Multi-ticker yfinance pull; verify the panel shape (~5,030 rows × 8 columns).
- Compute log-return panel; verify per-asset summary statistics are sane.
- Brief callback to Ch2 vocabulary (covariance, volatility, regime).
- Introduce the **covariance matrix Σ** as "the natural N-asset generalization of σ from Ch2." Diagonal = variances; off-diagonals = covariances.

### §2. Part I — Pairwise correlation (the textbook tool)

**§2.1 Pearson correlation defined.**

> *ρ<sub>XY</sub>* = Cov(*X*, *Y*) / (*σ<sub>X</sub> σ<sub>Y</sub>*)

The unitless cousin of covariance. Why divide by the product of standard deviations? Because covariance scales with the units of *X* and *Y* (a covariance computed on percent returns is different from one on basis-point returns); the normalization removes that. Bounded in [−1, +1] — proof in collapsible `<details>` (Cauchy–Schwarz).

**§2.2 What different correlations look like.** Three side-by-side scatter plots of daily log returns:
- SPY vs XLK (~0.9): tight diagonal cloud — these are nearly the same asset.
- SPY vs XLU (~0.6–0.7): correlated cloud, but visibly looser.
- SPY vs TLT (long-run near-zero): blob with no diagonal — the directions are genuinely independent on average.

Each scatter annotated with its computed *ρ*.

**§2.3 What this means with $100k.** A reader who buys $100k of SPY and adds $100k of XLK to "diversify" has nearly doubled their position size in the same risk; portfolio vol is roughly 1.95× the single-asset vol, not √2 ≈ 1.41×. Adding $100k of TLT instead — at correlation near zero — *does* roughly track √2. Concrete numbers worked out in the body.

### §3. Part II — Aggregation: portfolio variance and the diversification math

**§3.1 The two-asset portfolio variance formula.**

> *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

`where:` legend defining each symbol. The cross-term `2 w_X w_Y σ_X σ_Y ρ` is where diversification lives — when *ρ* < 1, this term shrinks the total variance below the weighted average. Derivation from definitions of variance/covariance in collapsible `<details>`.

**§3.2 The correlation matrix.** Compute and display the 8×8 correlation matrix as a heatmap (matplotlib `imshow` with annotations). Reading exercises: identify the sector-ETF block (high mutual correlation), spot the SPY-TLT cell (near-zero), spot the GLD column (low correlations all around).

**§3.3 The diversification math empirically.** Plot annualized vol of an equal-weighted basket as N grows from 1 to 8 (in some sensible order). Two regimes visible:
- Adding tightly-correlated names (sector ETFs to a sector ETF): vol drops modestly.
- Adding decorrelated names (TLT, GLD to the equity basket): vol drops noticeably.

Cite the **√N rule** (the limit if assets were uncorrelated) and the **diversification floor** (the limit if assets share a common correlation *ρ*: variance ratio approaches *ρ* as N → ∞). Floor formula in collapsible details.

**§3.4 Matrix form.** Promote the two-asset formula to general N:

> *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w**

where **Σ** is the covariance matrix and **w** is the weight vector. The compact form scales to any number of assets and is the building block for everything in modern portfolio theory. Linear-algebra derivation in collapsible details.

**§3.5 What this means with $100k.** Concrete portfolio comparisons, all dollar-translated:
- All-SPY: vol ~19% → ~$19k typical-year swing on $100k.
- 60/40 SPY/TLT: vol ~Z%; → ~$Zk swing.
- Equal-weighted 5 sector ETFs: vol ~W% (slightly lower than SPY, not by much).
- Equal-weighted 8 (sectors + cross-asset): vol ~U%, the lowest of the bunch.

Numbers will be filled in at implementation time from the actual data.

### §4. Part III — Regime / crisis correlation (the empirical wrinkle)

**§4.1 Rolling 60-day correlation between SPY and TLT.** Plot through 20 years. Visible features: persistently negative through 2008–2019 (TLT was a real hedge), brief positive spike March 2020 (everything crashed), sustained positive 2022 (rate-driven sell-off in both stocks and bonds). Caption: *"the bond hedge unhedged itself."*

**§4.2 Conditional correlation.** Compute the correlation between SPY and each other asset, conditional on:
- All days,
- The worst 5% of SPY days (left-tail conditioning).

Plot side-by-side bars. Correlations rise nearly across the board on bad days. The TLT bar is the most dramatic — its near-zero unconditional correlation rises substantially in stress.

**§4.3 Heatmap diptych — calm vs crisis.** Two 8×8 correlation heatmaps side by side: 2017 (calm) and Mar–Jun 2020 (crisis). Calm has visible structure (sector blocks distinct, cross-asset assets distinct). Crisis is uniformly red — *everything correlates in a panic*.

**§4.4 What this means.** The empirical finding stated plainly: *diversification works in normal times and fails in crises, which is exactly when you'd hoped it would work.* This **is** correlation-risk-as-a-flavor — a property of the world that pairwise correlations and a static covariance matrix can't capture on their own. Time-varying correlation models (DCC-GARCH) are named here as a deferred topic.

### §5. What we just learned (recap organized by concept-flavor)

Three subsections, one per covered flavor, each one paragraph:
- **Pairwise correlation** — what was learned about co-movement of pairs.
- **Aggregation / portfolio risk** — what was learned about combining many.
- **Regime / crisis correlation** — what was learned about correlation's non-stationarity.

Plus a closing paragraph on the two **deferred flavors** (factor exposure, tail dependence) so the reader knows what's still beyond the chapter.

### §6. Up next, Key Terms, Exercises

**Up next:** Chapter 4 — risk metrics (drawdown, VaR, Sharpe). Pays the Ch1 max-drawdown promise.

**Key Terms** table covering all new vocabulary. **Exercises** (4, in Ch1/Ch2 style):
1. **Different basket.** Re-run with crypto (`BTC-USD`, `ETH-USD`) added. Are correlations between crypto and stocks higher or lower than between stocks and bonds?
2. **The pre-2020 vs post-2020 SPY/TLT story.** Compute SPY/TLT correlation on the 2003–2019 window vs the 2020–present window. What changed?
3. **Conditional on TLT.** Repeat the §4.2 conditional-correlation exercise but conditioning on the worst 5% of *TLT* days instead of SPY days. Does the same "everything correlates" pattern emerge, or is it asymmetric?
4. *(stretch)* Pick three tickers you actually own (or would own). Compute pairwise correlations. Does the basket diversify as much as you thought?

## 6. New terminology

| Term | Brief meaning |
|---|---|
| Pearson correlation (*ρ*) | Covariance normalized by the product of standard deviations; in [−1, +1]. |
| Correlation matrix | Square symmetric matrix of pairwise correlations between N assets. |
| Covariance matrix (Σ) | Square symmetric matrix of pairwise covariances; diagonal is variances. |
| Portfolio weights (**w**) | Vector of allocations (sum to 1 for a long-only fully-invested portfolio). |
| Portfolio variance / std (σ<sub>p</sub>) | Variance / std of the weighted basket return. |
| Diversification benefit | The reduction in portfolio vol below the weighted average of individual vols, attributable to ρ < 1. |
| Equal-weight portfolio | Each asset gets weight 1/N. |
| 60/40 portfolio | Canonical 60% stocks / 40% bonds; classical "balanced" allocation. |
| √N rule | Equal-weighted vol of N uncorrelated assets is σ/√N. |
| Diversification floor | When pairwise correlations share a common value ρ, σ<sub>p</sub>²/σ² → ρ as N → ∞. |
| Systematic risk | The risk that *can't* be diversified away — common factor exposure. |
| Idiosyncratic risk | The portion of an asset's risk specific to it; can be diversified away. |
| Conditional correlation | Correlation computed on a subset of observations (e.g., worst-5%-of-SPY days). |
| Rolling correlation | Pairwise correlation computed over a sliding window. |
| Crisis correlation | Informal name for the empirical fact that pairwise correlations rise during stress. |
| Hidden factor exposure | When seemingly distinct assets share underlying drivers; named-but-deferred flavor. |
| Tail dependence | When correlations only manifest in the tails of the joint distribution; named-but-deferred flavor. |

## 7. New formulas (each with `where:` legend)

1. **Pearson correlation** — *ρ<sub>XY</sub>* = Cov(*X*, *Y*) / (*σ<sub>X</sub> σ<sub>Y</sub>*).
2. **Two-asset portfolio variance** — *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*.
3. **Matrix form** — *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w**.
4. **√N rule** — *σ<sub>p</sub>* = *σ* / √*N* for equal-weighted uncorrelated assets.
5. **Diversification floor** — *σ<sub>p</sub>²* / *σ²* → *ρ* as *N* → ∞ when all pairwise correlations equal *ρ*.

Heavier derivations (Cauchy–Schwarz proof of the [−1, +1] bound; algebraic derivation of the two-asset formula; the matrix form; the floor result) live in collapsible `<details>` blocks per the established convention.

## 8. Code structure and dependencies

- `03-correlation/README.md` — chapter prose, end-of-chapter Key Terms.
- `03-correlation/lesson.ipynb` — runnable notebook with just-in-time micro-explanations.
- Append new entries to root `glossary.md` (alphabetized, tagged Ch. 3).

### Dependencies

**No new packages.** numpy/pandas/matplotlib/yfinance/scipy already cover everything. Heatmaps via matplotlib's `imshow` directly — no seaborn dependency.

### No new helpers / no shared module

Each chapter remains self-contained. Re-do the data download in the Ch3 notebook.

## 9. Conventions to follow

Inherited from prior chapters (see `MEMORY.md` feedback memories):

- Define every domain term on first use (inline blockquote gloss).
- Define every formula symbol via a `where:` legend.
- Inline glosses + chapter Key Terms table + glossary append.
- Notebook cells get just-in-time micro-explanations; deeper "why" lives in the README.
- Heavier math goes in collapsible `<details>` blocks.
- HTML subscripts (`<sub>`) for formula rendering.
- **Concept-before-statistic:** opening "What we mean by X" framing; concrete dollar / lived-experience translations after every major statistical finding; recap organized by concept-flavor.

## 10. Cross-chapter promises honored

- Ch1 README curriculum line — *"Chapter 3: Multiple assets — correlation and diversification"* → entire chapter.
- Ch2 §3.2 covariance gloss — *"will reappear as the central object of Chapter 3 (correlation between assets)"* → §1 setup connects covariance matrix to Ch2's covariance, §2 builds correlation directly from it.
- Ch2 framing — *"Correlation risk is the entire subject of Chapter 3"* → opening concept-flavors section names the slate of correlation-risk flavors.

## 11. Cross-chapter promises NOT honored (with rationale)

- Ch1 §5 drawdown gloss (*"max drawdown ... we'll formalize later"*) — still owed; **Chapter 4 risk-metrics** is its natural home.
- Ch2-deferred topics (GARCH, EVT) — still deferred to dedicated chapters.

## 12. Edits required to existing files (Ch2 + root)

- Ch2 README "Up next" — already states the chapter has correlation as its subject, but should be updated to reflect Ch3's actual title and a one-line preview of the three concept-flavors (pairwise, aggregation, regime).
- Top-level `README.md` curriculum table — Ch3 row swapped from "_coming next_" to its full title with a link, in the same format as Ch2's row.

## 13. Open questions

None at design-approval time. Implementation may surface small choices (exact rolling-correlation window length, exact conditional-correlation threshold percentile, the order of tickers in the §3.3 add-one-at-a-time vol plot) — all routine implementation calls.
