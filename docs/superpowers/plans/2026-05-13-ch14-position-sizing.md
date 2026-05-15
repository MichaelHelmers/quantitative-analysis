# Chapter 14 Implementation Plan — Position Sizing & Risk of Ruin

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Chapter 14 — paired notebook + README — that opens Part 8 by sizing a *stipulated* positive-EV strategy three ways (per-trade Kelly, per-period vol targeting, equity-curve drawdown stops), simulates ruin probability via Monte Carlo and EVT-extrapolated GPD, and emits a single side-by-side rule-comparison table. The EVT salvage from retired Ch10 lands here as a tight §6 sidebar.

**Architecture:** `14-position-sizing/`. No new external data; everything is generated from a seeded `numpy.random.default_rng(14)` against stipulated `(μ=1.0 bp, σ=7.0 bp, trades/session=6, sessions/year=252)`. Reuses the Ch5 drawdown helper (running peak → drawdown series → MDD) on simulated equity paths. EVT sidebar uses `scipy.stats.genpareto`.

**Tech Stack:** Python 3.11+, pandas, numpy, matplotlib, scipy. No new deps.

**Spec reference:** `docs/superpowers/specs/2026-05-13-ch14-position-sizing-design.md`

**Honest-data working targets:**

| Quantity | Working target | Notes |
|---|---|---|
| Stipulated per-trade Sharpe | 0.143 | μ/σ = 1.0 / 7.0 |
| Stipulated annualized Sharpe (unit notional) | ~5.6 | 0.143 × √(6·252); unrealistic by design |
| Full-Kelly fraction f\* | ~0.020 per trade | μ/σ² = 1e-4 / 4.9e-3 |
| Full-Kelly growth-rate g\* | ~1.0e-4 per trade | ≈ ½ · μ²/σ² |
| MC mean final equity, full-Kelly | 1.4–1.8× starting | annual horizon, 252·6=1,512 trades |
| MC p95 max DD, full-Kelly | 35–55% | classical Kelly-DD pain |
| MC p95 max DD, half-Kelly | 18–28% | roughly halves |
| Vol-target leverage at τ=10%/yr | 5–10× (varies w/ σ̂) | sanity-check before §4 worked example |
| EVT GPD ξ̂ on i.i.d. Normal tail | ~0 (Gumbel domain) | thin-tail confirmation |
| EVT vs MC P(DD ≥ 20%) | within ±20% relative | sanity agreement |
| EVT vs MC P(DD ≥ 50%) | MC ≈ 0, EVT small-positive | extrapolation payoff |

**Computational sanity:** 10,000 MC paths × 1,512 trades each = 1.5e7 ops, vectorized via NumPy. Should run < 20s. GPD fit + sweep across 4 DD thresholds is sub-second.

---

## File map

| File | Status |
| --- | --- |
| `14-position-sizing/lesson.ipynb` | create |
| `14-position-sizing/lesson_merged.ipynb` | create |
| `14-position-sizing/README.md` | create |
| `glossary.md` | modify |
| `README.md` (root) | modify |
| Memory roadmap | modify |

---

## Task 1: Pre-flight numerics

- [ ] **Step 1.1:** Create the chapter directory.

Run: `mkdir -p 14-position-sizing`

- [ ] **Step 1.2: Write `/tmp/ch14_numbers.py`**

```python
"""Pre-flight for Ch14: Kelly, fractional Kelly, fixed-fractional, vol targeting,
drawdown stops, MC + EVT risk-of-ruin. Stipulated synthetic strategy."""
import numpy as np
import pandas as pd
from scipy.stats import genpareto
from scipy.optimize import brentq

rng = np.random.default_rng(14)

# === Stipulated strategy ===
MU_BP = 1.0           # per-trade mean, basis points
SIGMA_BP = 7.0        # per-trade std, basis points
TRADES_PER_SESSION = 6
SESSIONS_PER_YEAR = 252
TPY = TRADES_PER_SESSION * SESSIONS_PER_YEAR   # 1,512 trades/year
N_PATHS = 10_000

mu = MU_BP / 1e4      # 1e-4 in return units
sigma = SIGMA_BP / 1e4

per_trade_sharpe = mu / sigma
ann_sharpe_unit = per_trade_sharpe * np.sqrt(TPY)
print(f"Per-trade Sharpe: {per_trade_sharpe:.4f}")
print(f"Annualized Sharpe (unit notional): {ann_sharpe_unit:.3f}")

# === §2 Kelly ===
f_kelly = mu / sigma**2
g_kelly = 0.5 * mu**2 / sigma**2   # ½·μ²/σ² growth rate at f*
print(f"Full-Kelly f* per trade: {f_kelly:.6f}  (~{f_kelly*100:.2f}% of equity)")
print(f"Full-Kelly growth rate g*: {g_kelly:.6e} per trade")
print(f"Annualized growth at full-Kelly: {g_kelly * TPY:.4f}  (~{(np.exp(g_kelly*TPY)-1)*100:.1f}%)")

# Growth vs leverage multiplier k (k=1 is full-Kelly, k=2 is overbet to zero growth)
k_grid = np.linspace(0, 3, 61)
g_k = (k_grid * f_kelly) * mu - 0.5 * (k_grid * f_kelly)**2 * sigma**2

# === §3 Fixed-fractional ===
# Risk 2% of equity per trade, stop distance d = 1·sigma (1-bp-σ-units? Use σ in returns.)
RISK_PER_TRADE = 0.02
STOP_DIST = sigma  # 1σ stop in return units
f_fixed_frac = RISK_PER_TRADE / STOP_DIST
print(f"Fixed-fractional (2% risk, 1σ stop) fraction: {f_fixed_frac:.4f}")
# Note: fixed-fractional ignores μ — much larger than Kelly because Kelly's
# denominator is σ² (huge in fraction-of-equity terms) not σ.

# === §4 Vol targeting ===
# Daily PnL std at unit notional = σ_trade · √(trades/session)
sigma_daily = sigma * np.sqrt(TRADES_PER_SESSION)
TARGET_DAILY_VOL = 0.01   # 1% daily
target_lev = TARGET_DAILY_VOL / sigma_daily
print(f"Daily PnL std (unit notional): {sigma_daily*1e4:.2f} bp")
print(f"Vol-target leverage at 1% daily vol: {target_lev:.2f}×")

# === Simulate MC paths under each rule ===
# 10,000 paths × 1,512 trades. r_t ~ N(mu, sigma²). Equity multiplied by (1 + f·r_t).
all_returns = rng.normal(mu, sigma, size=(N_PATHS, TPY))

def equity_curves(f_per_trade, returns):
    """Compound equity under fixed per-trade leverage f."""
    eq = np.cumprod(1.0 + f_per_trade * returns, axis=1)
    eq = np.concatenate([np.ones((eq.shape[0], 1)), eq], axis=1)
    return eq

def max_drawdown(eq):
    """Max drawdown across each row of an equity matrix."""
    peak = np.maximum.accumulate(eq, axis=1)
    dd = (eq - peak) / peak
    return -dd.min(axis=1)   # positive number, fraction

def summarize(eq, label):
    mdd = max_drawdown(eq)
    final = eq[:, -1]
    # Equity Sharpe: (mean log-return) / (std log-return) × √(periods/year)
    # On per-trade equity series:
    per_trade_log = np.diff(np.log(eq), axis=1)
    s = per_trade_log.mean(axis=1) / per_trade_log.std(axis=1) * np.sqrt(TPY)
    return {
        "rule": label,
        "mean_final": final.mean(),
        "median_mdd": np.median(mdd),
        "p95_mdd": np.quantile(mdd, 0.95),
        "frac_dd_ge_20pct": (mdd >= 0.20).mean(),
        "frac_dd_ge_50pct": (mdd >= 0.50).mean(),
        "mean_sharpe": s.mean(),
    }

rows = []
for label, f in [
    ("Unit notional", 1.0),
    ("Full Kelly", f_kelly),
    ("Half Kelly", 0.5 * f_kelly),
    ("Quarter Kelly", 0.25 * f_kelly),
    ("Fixed-fractional 2%", f_fixed_frac),
    ("Vol-target 10% (≈ τ_daily=0.63%)", 0.0063 / sigma_daily),
]:
    eq = equity_curves(f, all_returns)
    rows.append(summarize(eq, label))

# Drawdown-stop variants: halve f on 5% DD until recovered within 2% of peak;
# halt on 10% DD entirely. Implement on the half-Kelly base.
def simulate_with_stop(f0, returns, halve_at=0.05, recover_within=0.02, halt_at=None):
    eq = np.ones((returns.shape[0], returns.shape[1] + 1))
    peak = np.ones(returns.shape[0])
    halved = np.zeros(returns.shape[0], dtype=bool)
    halted = np.zeros(returns.shape[0], dtype=bool)
    for t in range(returns.shape[1]):
        f_eff = np.where(halted, 0.0, np.where(halved, 0.5 * f0, f0))
        eq[:, t + 1] = eq[:, t] * (1.0 + f_eff * returns[:, t])
        peak = np.maximum(peak, eq[:, t + 1])
        dd = (peak - eq[:, t + 1]) / peak
        if halt_at is not None:
            halted |= dd >= halt_at
        halved = (halved | (dd >= halve_at)) & (dd > recover_within)
    return eq

eq_hk_halve = simulate_with_stop(0.5 * f_kelly, all_returns, halve_at=0.05, recover_within=0.02)
rows.append(summarize(eq_hk_halve, "Half-Kelly + halve-on-5%"))
eq_hk_halt = simulate_with_stop(0.5 * f_kelly, all_returns, halt_at=0.10)
rows.append(summarize(eq_hk_halt, "Half-Kelly + halt-on-10%"))

df = pd.DataFrame(rows)
print("\n=== Side-by-side comparison ===")
print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# === §6 EVT risk-of-ruin sidebar ===
# Fit GPD to the lower tail of per-trade returns (left tail = losses).
losses = -all_returns.flatten()   # losses are positive
u = np.quantile(losses, 0.95)
tail = losses[losses > u] - u
xi_hat, _, sigma_hat = genpareto.fit(tail, floc=0)
print(f"\nGPD fit on synthetic left tail (u=p95): ξ̂={xi_hat:+.3f}, σ̂={sigma_hat:.6e}")
# Empirical MC P(DD ≥ X) for X in {0.10, 0.20, 0.30, 0.50}
mdd_full = max_drawdown(equity_curves(f_kelly, all_returns))
for X in [0.10, 0.20, 0.30, 0.50]:
    p_mc = (mdd_full >= X).mean()
    print(f"  P_MC(DD ≥ {X*100:.0f}% | full-Kelly) = {p_mc:.4f}")

# Student-t for Exercise 3
rng_t = np.random.default_rng(99)
DF = 4
t_raw = rng_t.standard_t(DF, size=(N_PATHS, TPY))
t_scale = sigma * np.sqrt((DF - 2) / DF)   # match variance
t_returns = mu + t_scale * t_raw
losses_t = -t_returns.flatten()
u_t = np.quantile(losses_t, 0.95)
tail_t = losses_t[losses_t > u_t] - u_t
xi_t, _, sigma_t = genpareto.fit(tail_t, floc=0)
print(f"GPD fit on Student-t(df=4) left tail: ξ̂={xi_t:+.3f}, σ̂={sigma_t:.6e}")
```

- [ ] **Step 1.3:** Run, save outputs to `/tmp/ch14_findings.md` with sections:
  - Stipulated strategy headline numbers (per-trade + annualized Sharpe).
  - Full-Kelly fraction + growth rate, vs k-multiplier curve.
  - Fixed-fractional fraction at 2% risk / 1σ stop.
  - Vol-target leverage at τ_daily=1%.
  - Side-by-side comparison table (mean final, median MDD, p95 MDD, P(DD≥20%), P(DD≥50%), mean Sharpe) — 8 rows.
  - GPD ξ̂ on Normal vs Student-t tails.
  - MC P(DD ≥ X) at X ∈ {10%, 20%, 30%, 50%} under full-Kelly.

- [ ] **Step 1.4: Course-correction watchlist** — document any of these that fire:
  - **Vol-target leverage > 20×.** Lower the target_vol used in worked examples to keep equity paths sensible. Note that the framework — not the specific number — is what generalizes.
  - **Half-Kelly p95 MDD < 25%.** "Half-Kelly is the sweet spot" may need to shift toward quarter-Kelly. Update §2.5 / §7 narrative.
  - **Drawdown stops reduce expected growth more than they reduce p95 MDD.** Reframe §5 around "stops are insurance against the i.i.d. assumption being wrong," forward-pointing to Ch15 regime detection.
  - **EVT vs MC disagree at P(DD ≥ 20%) by more than ±30% relative.** Likely a threshold or block-size issue in the GPD fit — re-run at u = p90 / p95 / p97.5 and pick the most defensible.
  - **Student-t GPD ξ̂ ≈ Normal GPD ξ̂.** Means EVT can't tell the two distributions apart on this sample size — turn that into the actual lesson and update Exercise 3 narrative.

- [ ] **Step 1.5:** Checkpoint — pause before notebook build.

---

## Task 2: Terse lesson notebook

Build `14-position-sizing/lesson.ipynb` via `build_ch14_notebook.py`. The terse notebook is code-heavy; prose lives in the README. Cells use the same `cell_id` convention as Ch11-13.

Cell list:

- `title` (markdown) — title + spec link + chapter overview (3 sentences).
- `s1-head` + `s1-setup` (markdown + code) — stipulated strategy parameters; print per-trade and annualized Sharpe.
- `s1-equity-baseline` (code) — single unit-notional sample path equity plot.
- `s2-head` + `s2-kelly-derivation-stub` (markdown) — Bernoulli form, continuous form, where-clauses.
- `s2-kelly-numbers` (code) — compute f\*, g\*, growth-vs-k curve, plot.
- `s2-half-kelly` (code) — half-Kelly and quarter-Kelly p95-MDD comparison.
- `s3-head` + `s3-fixed-fractional` (markdown + code) — fixed-fractional fraction; comparison with Kelly when stop_dist is constant.
- `s4-head` + `s4-vol-target` (markdown + code) — vol-target formula + leverage at τ_daily=1%; sample path.
- `s5-head` + `s5-mc-fans` (markdown + code) — fan chart (p5 / p50 / p95) for each of {unit, full-Kelly, half-Kelly, quarter-Kelly, vol-target}.
- `s5-mc-stops` (code) — same MC paths with halve-on-5% and halt-on-10% applied; fan chart overlay for half-Kelly base.
- `s6-head` + `s6-gpd-fit` (markdown + code) — GPD fit on Normal tail; print ξ̂; QQ-plot of GPD vs empirical tail.
- `s6-evt-vs-mc` (code) — table of P(DD ≥ X) at X ∈ {10%, 20%, 30%, 50%} from MC vs EVT extrapolation.
- `s6-student-t` (code) — same fit on Student-t(df=4) returns for Exercise 3 setup.
- `s7-summary-table` (markdown + code) — final side-by-side rule-comparison table.
- `s8-head` (markdown) — So what + Key Terms + Up next (Ch15 σ̂_t refinement; Ch16 real candidates).
- `exercises` (markdown) — 4 prompts.
- `ex1-solution` + `ex3-solution` (code + markdown) — worked solutions for Exercises 1 and 3 only (per spec; 2 and 4 stay as prompts).

- [ ] **Step 2.1: Write `build_ch14_notebook.py`**

```python
"""Build 14-position-sizing/lesson.ipynb."""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

def md(cid, text):
    c = nbf.v4.new_markdown_cell(text)
    c.metadata["id"] = cid
    cells.append(c)

def code(cid, src):
    c = nbf.v4.new_code_cell(src)
    c.metadata["id"] = cid
    cells.append(c)

md("title", """# Chapter 14 — Position Sizing & Risk of Ruin

Spec: `docs/superpowers/specs/2026-05-13-ch14-position-sizing-design.md`

Three questions: how much per trade (Kelly), how much per unit time (vol targeting),
and when to stop (drawdown stops + risk of ruin).""")

md("s1-head", """## §1 — Setup: stipulated strategy

Ch13 closed at after-execution Sharpe −1.11 ⇒ Kelly = 0 on that strategy. To
have something to size against, we stipulate a positive-EV cousin: μ = 1 bp,
σ = 7 bp, 6 trades/session, 252 sessions/year. Ch16 will hunt for a real
candidate.""")

code("s1-setup", """\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import genpareto

rng = np.random.default_rng(14)

# Stipulated strategy parameters (basis points → fractional returns)
MU_BP, SIGMA_BP = 1.0, 7.0
TPS, SPY = 6, 252                  # trades/session, sessions/year
TPY = TPS * SPY                    # trades/year = 1,512
N_PATHS = 10_000

mu, sigma = MU_BP / 1e4, SIGMA_BP / 1e4
per_trade_sharpe = mu / sigma
ann_sharpe_unit = per_trade_sharpe * np.sqrt(TPY)
print(f"Per-trade Sharpe: {per_trade_sharpe:.4f}")
print(f"Annualized Sharpe (unit notional): {ann_sharpe_unit:.3f}")
""")

# ... [remaining cells follow the same pattern — paste pre-flight code blocks
#      verbatim, splitting at section boundaries. Each cell starts with a
#      short # comment naming the section.]

# (See Step 1.2 pre-flight script for the full code library; this builder
#  partitions that script into the cell list above.)

Path("14-position-sizing/lesson.ipynb").write_text(nbf.writes(nb))
print("wrote lesson.ipynb")
```

- [ ] **Step 2.2:** Complete the builder by pasting each pre-flight code block into its `code(...)` cell exactly as run in Step 1.2 (do not re-derive; copy verbatim so notebook numbers exactly match the pre-flight). Add per-cell `# ...` comments on non-obvious lines per `feedback_comment_nonobvious_code`: name the formula being computed, the MC vectorization trick, the GPD fit threshold choice.

- [ ] **Step 2.3:** Run `python build_ch14_notebook.py && jupyter nbconvert --execute --inplace 14-position-sizing/lesson.ipynb`. Confirm zero errors. Spot-check that the printed Kelly fraction, MC table, and EVT ξ̂ match `/tmp/ch14_findings.md` exactly.

- [ ] **Step 2.4: Commit checkpoint.** Do not stage yet; pause for review.

---

## Task 3: README

Build `14-position-sizing/README.md` matching spec §1–§8. README carries the prose; the notebook carries the numbers.

Required content per section:

- **§1 Setup.** Honest disclaimer (Ch13 → Kelly=0). Stipulated parameters table. Three operational questions framed up front (per-trade, per-period, when-to-stop).
- **§2 Kelly.** Bernoulli form + continuous form with where-clauses for every symbol (f, p, q, b, μ, σ, r). Derivation in `<details>` block (Taylor expansion of E[log(1+f·r)]). Worked f\* on stipulated strategy. Three reasons to under-bet (estimation, fat tails, max-DD). Growth-vs-k plot interpretation paragraph per `feedback_push_interpretations_past_description`.
- **§3 Alternatives.** Fixed-fractional formula `size = (r · equity) / d` with where-clause. Fixed-dollar baseline. Comparison narrative on when fixed-fractional and Kelly diverge.
- **§4 Vol targeting.** `size_t = (τ_daily · equity) / σ̂_t` with where-clause. Choice of σ̂_t (rolling 20-day, with forward-pointer to Ch15). Regime-sensitivity paragraph. Relation-to-Kelly paragraph.
- **§5 Drawdown control.** Fan-chart interpretation per rule. Drawdown-stop rule definitions (halve-on-5%, halt-on-10%) with where-clauses on the trigger thresholds. Honest behavioral caveat.
- **§6 EVT sidebar.** GPD density with where-clause (ξ, σ_GPD, threshold u). Two-method comparison (MC vs EVT). Headline finding (Normal: ξ̂≈0, MC and EVT agree at moderate DD; EVT extrapolates beyond MC reach at deep DD).
- **§7 Side-by-side table.** Reproduce the table from the notebook with the actual numbers.
- **§8 So what + Key Terms + Up next.** Three decision rules. Forward pointers to Ch15 (σ̂_t refinement) and Ch16 (real candidates).

**Key Terms (target 10):** bet size, leverage, Kelly criterion, full Kelly, fractional Kelly, fixed-fractional sizing, volatility targeting, drawdown stop, risk of ruin, expected log-wealth growth rate.

**Cross-chapter linking (per `feedback_define_every_term` + author's voice):**
- Ch5 drawdown machinery reused on equity curves (cross-link to Ch5 §2).
- Ch7 §1 expectancy connects to Bernoulli Kelly's edge/odds quantity.
- Ch10 EVT preview from retired chapter formalized in §6.
- Ch11 walk-forward ledger informs stipulated parameters (footnote in §1).

**Exercise prompts** (final block of README, matching notebook 1:1 per `feedback_exercises_bottom_and_matched`):

1. **Kelly's sensitivity to μ misestimate.** Vary μ̂ by ±1 SE (SE = σ/√1500 ≈ 1.81e-4 in fractional return units). Plot f\*(μ̂) and growth-rate g(f\*(μ̂)) using true μ. Show that +1-SE optimistic μ̂ produces ~2× full-Kelly leverage and negative growth at full-Kelly.
2. **Vol targeting under regime shift.** Generate a synthetic 1-year session-bar series where true σ doubles at t=0.5. Run vol targeting with 20-day rolling σ̂_t and target_daily_vol=1%. Plot realized-vol vs target-vol; document the lag (in days) before realized catches up, and the over-leveraged window's max DD.
3. **Empirical-MC vs GPD-extrapolated P(DD ≥ 20%).** Compute both on the stipulated strategy. Then redo with Student-t(df=4) per-trade returns at matched variance. Document the gap that opens at deep-DD thresholds (P(DD ≥ 30%), P(DD ≥ 50%)).
4. **Half-Kelly vs vol-target at matched ex-ante leverage.** Pick target_vol such that vol-target's average leverage equals half-Kelly's leverage (~0.5 · f\* · expected per-trade equity). Compare max-DD distributions and equity Sharpes. Which is preferable and why?

Worked solutions for 1 and 3 in the notebook only; 2 and 4 stay as prompts.

- [ ] **Step 3.1:** Draft README section-by-section. Use the `<details>`-block convention from Ch4/Ch5/Ch7 for the Kelly Taylor derivation.
- [ ] **Step 3.2:** Verify exercise prompts in README are byte-for-byte identical to those in the notebook `exercises` cell.
- [ ] **Step 3.3:** Run the README's `<details>` math through a quick mental walk to confirm symbols resolve. Cross-reference where-clauses.
- [ ] **Step 3.4:** Checkpoint.

---

## Task 4: Merged notebook

Build `14-position-sizing/lesson_merged.ipynb` interleaving the README prose and the lesson notebook's code cells. Same builder pattern as Ch10/Ch11/Ch12/Ch13.

Layout: title → §1 prose → §1 code → §2 prose → §2 code (Kelly derivation `<details>` lives inside the prose cell) → ... → §8 prose → exercises prompt → worked solution cells for Ex1 and Ex3 (per spec: worked solutions follow prompts but nothing else does, per `feedback_exercises_bottom_and_matched`).

- [ ] **Step 4.1: Write `build_ch14_merged.py`** importing the cell library used by the lesson builder. Re-use the same cell IDs so cross-referencing between the two notebooks is mechanical.

- [ ] **Step 4.2:** Run the build + execute via `jupyter nbconvert --execute --inplace`. Confirm zero errors.

- [ ] **Step 4.3:** Verify exercise prompts are byte-identical across README / lesson / merged.

- [ ] **Step 4.4:** Checkpoint.

---

## Task 5: Glue updates + commit

- [ ] **Step 5.1: `glossary.md`** — add 10 Key Terms with one-line definitions: bet size, leverage, Kelly criterion, full Kelly, fractional Kelly, fixed-fractional sizing, volatility targeting, drawdown stop, risk of ruin, expected log-wealth growth rate. Append to bottom of file; do not re-order existing entries.

- [ ] **Step 5.2: Root `README.md`** — add the Ch14 row to the chapter index table. Follow the format of Ch12/Ch13 rows (chapter number, title, one-line description, link to subdir).

- [ ] **Step 5.3: Update `MEMORY.md` / `project_curriculum_roadmap.md`** Ch14 entry with:
  - Spec + plan paths.
  - Three-flavor framing.
  - Covered with empirical headlines (Kelly f\*, MC p95 MDD per rule, EVT ξ̂, side-by-side table).
  - Mid-execution course corrections (if any fired from Step 1.4's watchlist).
  - Promises honored (Ch11 §7, Ch12 negative-budget, Ch13 framework-still-matters, Pivot 2026-05-07 EVT salvage, Ch5 drawdown, Ch7 expectancy).
  - Promises to honor in later chapters (Ch15 σ̂_t, Ch16 real-candidate sizing, Ch17-18 contract-granularity Kelly).

- [ ] **Step 5.4: Commit.** Stage only Ch14 paths explicitly per `feedback_isolate_in_progress_chapters`:

```bash
git add 14-position-sizing/ \
        docs/superpowers/specs/2026-05-13-ch14-position-sizing-design.md \
        docs/superpowers/plans/2026-05-13-ch14-position-sizing.md \
        glossary.md README.md
git diff --cached --stat   # verify no sibling-chapter files staged
git commit -m "$(cat <<'EOF'
Add Chapter 14 — Position sizing and risk of ruin

Opens Part 8 with the sizing question: given a positive-EV strategy,
how much to commit per trade (Kelly + fractional Kelly + fixed-fractional),
per unit time (vol targeting), and when to stop (drawdown stops + EVT risk of ruin).
Strategy is stipulated synthetic because Ch13 closed at Kelly=0.
EVT sidebar pays the retired-Ch10 salvage debt from the 2026-05-07 pivot.
EOF
)"
```

- [ ] **Step 5.5:** Run `git status` and confirm a clean tree. Update memory file `MEMORY.md` to mark Ch14 entry as ✅ DONE with today's date.

---

## Self-review checklist

After implementation completes, before declaring the chapter done:

- [ ] Spec coverage: §1 setup → s1 cells; §2 Kelly → s2 cells; §3 alternatives → s3; §4 vol target → s4; §5 drawdown → s5; §6 EVT → s6; §7 table → s7; §8 + Key Terms + Up next → s8 + glossary update. Every spec section traces to at least one notebook cell and one README section.
- [ ] Placeholder scan: search README/notebook for "TBD", "TODO", "see above", "fill in" — fix any.
- [ ] Symbol consistency: `μ`, `σ`, `f`, `f*`, `r`, `g(f)` used identically across README math and notebook code variable names (`mu`, `sigma`, `f_kelly`, `g_kelly`).
- [ ] All four exercises appear byte-identically in README / lesson / merged; worked solutions for 1 and 3 are present in lesson + merged, absent from README.
- [ ] All formulas have where-clauses per `feedback_define_formula_symbols`.
- [ ] No external-knowledge leaps per `feedback_no_external_knowledge_leaps` — log-wealth, GPD, Pareto tail, "growth rate" all glossed inline at first use.
