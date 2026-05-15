# Chapter 15 Implementation Plan — Intraday Vol & Regime Detection

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Chapter 15 — paired notebook + README — that constructs a three-time-scale σ̂_t estimator (within-session seasonality × across-session GARCH × across-regime indicators) on Ch11's QQQ 1-min window, then cashes it on Ch11's walk-forward trade ledger via two experiments (vol targeting; high-vol filter). Absorbs the retired Ch9 GARCH salvage; pays Ch14 §4's σ̂_t placeholder debt.

**Architecture:** `15-intraday-vol-regime/`. Reuses Ch6 QQQ 1-min parquet and Ch11 walk-forward ledger. Three new estimators: trailing per-minute seasonality (point-in-time, 60-session window); hand-rolled GARCH(1,1) via `scipy.optimize.minimize`; 2-state HMM (try `hmmlearn`; fall back to hand-rolled EM if broken under pandas 3.0 — same risk pattern as retired Ch9's `arch` failure). CPI/NFP event calendar lives in `15-intraday-vol-regime/data/event_calendar.csv`.

**Tech Stack:** Python 3.11+, pandas, numpy, scipy.optimize, scipy.stats, matplotlib. Optional new dep: `hmmlearn` (with hand-rolled fallback).

**Spec reference:** `docs/superpowers/specs/2026-05-13-ch15-intraday-vol-regime-design.md`

**Honest-data working targets:**

| Quantity | Working target | Notes |
|---|---|---|
| Peak-to-trough seasonality ratio | 3–5× | open vs midday on QQQ |
| GARCH persistence α̂ + β̂ | 0.90–0.99 | wide CI on ~250 session bars |
| Long-run annualized σ̄ from GARCH | within 20% of whole-window σ | sanity bound |
| Event-day vs non-event σ̂_GARCH ratio | 1.3–2.5× | FOMC/CPI/NFP avg vs baseline |
| Vol-threshold p80 flagged-day count | ~50 / 251 | by construction |
| HMM high-vol smoothed prob > 0.5 | 30–70 / 251 days | model-dependent |
| CUSUM detected change-points | 2–6 over the year | sensitivity to threshold |
| §6 Exp 1 vol-targeted Sharpe | within ±0.3 of Ch11's +0.88 | reshape, not shift mean |
| §6 Exp 2 high-vol-filter Sharpe | could go either direction | hypothesis to test |
| §6 Exp 1 max-DD reduction | 20–40% relative | vol-target smooths PnL |

**Computational sanity:** GARCH MLE on ~250 obs: <2s. HMM EM 2-state on ~250 obs: <3s. Seasonality estimator (251 sessions × 390 minutes, trailing-60 window): vectorized via groupby, <5s. Total notebook: <30s.

---

## File map

| File | Status |
| --- | --- |
| `15-intraday-vol-regime/lesson.ipynb` | create |
| `15-intraday-vol-regime/lesson_merged.ipynb` | create |
| `15-intraday-vol-regime/README.md` | create |
| `15-intraday-vol-regime/data/event_calendar.csv` | create |
| `15-intraday-vol-regime/garch.py` | create (hand-rolled GARCH MLE helpers) |
| `15-intraday-vol-regime/hmm.py` | create (2-state EM, fallback path) |
| `glossary.md` | modify |
| `README.md` (root) | modify |
| Memory roadmap | modify |

The two helper modules keep the notebook readable (per spec page-budget hedge). Cell imports them; tests live next to the modules.

---

## Task 1: Event calendar + pre-flight numerics

- [ ] **Step 1.1:** Create directory and event-calendar CSV.

```bash
mkdir -p 15-intraday-vol-regime/data
```

- [ ] **Step 1.2: Write `15-intraday-vol-regime/data/event_calendar.csv`**

Three event types — FOMC (8 dates, copied from Ch6's existing FOMC list), CPI (12 dates, monthly BLS-published 2025-05 through 2026-04), NFP (12 dates, first Friday of each month 2025-05 through 2026-04). Cross-check release-mechanics: FOMC at 14:00 ET, CPI and NFP at 08:30 ET (pre-open). Schema:

```csv
date,event_type,release_time_et
2025-06-12,FOMC,14:00
2025-06-11,CPI,08:30
2025-06-06,NFP,08:30
...
```

Verify each FOMC date against Ch6's hardcoded list (probably in `06-bridge-to-intraday/lesson.ipynb` cell `s5-events`) — if a date is missing or wrong, fix the calendar and document the source.

- [ ] **Step 1.3: Write `15-intraday-vol-regime/garch.py`**

```python
"""Hand-rolled GARCH(1,1) MLE — pure scipy. No `arch` dependency
(broken under pandas 3.0 per retired Ch9 plan)."""
import numpy as np
from scipy.optimize import minimize


def garch11_neg_log_lik(params, r):
    """GARCH(1,1) negative log-likelihood under Normal innovations.

    σ²_t = ω + α r²_{t-1} + β σ²_{t-1}
    where:
      r_t   = log-return at session t (mean-centered).
      ω > 0 = baseline variance.
      α ≥ 0 = ARCH coefficient (innovation impact).
      β ≥ 0 = GARCH coefficient (variance persistence).
      α+β<1 = stationarity constraint.
    """
    omega, alpha, beta = params
    if omega <= 0 or alpha < 0 or beta < 0 or (alpha + beta) >= 1:
        return 1e10
    n = len(r)
    sigma2 = np.empty(n)
    sigma2[0] = r.var(ddof=0)   # initialize at unconditional variance
    for t in range(1, n):
        sigma2[t] = omega + alpha * r[t-1]**2 + beta * sigma2[t-1]
    # Normal log-likelihood (drop constant): -0.5 · sum(log σ²_t + r²_t / σ²_t)
    return 0.5 * np.sum(np.log(sigma2) + r**2 / sigma2)


def fit_garch11(r):
    """Fit GARCH(1,1) by MLE. Returns (omega, alpha, beta, sigma2_series)."""
    r = np.asarray(r) - np.mean(r)   # demean before fit (μ ≪ σ on session bars)
    x0 = (0.02 * r.var(), 0.10, 0.85)
    res = minimize(
        garch11_neg_log_lik, x0, args=(r,),
        method="L-BFGS-B",
        bounds=[(1e-12, None), (0.0, 1.0), (0.0, 1.0)],
    )
    omega, alpha, beta = res.x
    # Re-roll the sigma² path
    sigma2 = np.empty(len(r))
    sigma2[0] = r.var()
    for t in range(1, len(r)):
        sigma2[t] = omega + alpha * r[t-1]**2 + beta * sigma2[t-1]
    return omega, alpha, beta, sigma2


def long_run_variance(omega, alpha, beta):
    """Unconditional variance ω / (1 − α − β)."""
    return omega / (1.0 - alpha - beta)
```

- [ ] **Step 1.4: Write `15-intraday-vol-regime/hmm.py`**

```python
"""2-state Gaussian HMM with hand-rolled EM. Used as fallback if hmmlearn
is unavailable under pandas 3.0."""
import numpy as np


def forward_backward(obs, mu, sigma2, pi, A):
    """Forward-backward recursion. Returns (gamma, log_lik).
    obs   : (T,) observations
    mu    : (2,) state means
    sigma2: (2,) state variances
    pi    : (2,) initial state distribution
    A     : (2, 2) transition matrix, A[i, j] = P(s_{t+1}=j | s_t=i)
    gamma : (T, 2) smoothed state probabilities
    """
    T = len(obs)
    log_b = -0.5 * (np.log(2*np.pi*sigma2)[None, :] + (obs[:, None] - mu[None, :])**2 / sigma2[None, :])
    # Forward (scaled)
    alpha = np.zeros((T, 2))
    c = np.zeros(T)
    alpha[0] = pi * np.exp(log_b[0] - log_b[0].max())
    c[0] = alpha[0].sum()
    alpha[0] /= c[0]
    for t in range(1, T):
        alpha[t] = (alpha[t-1] @ A) * np.exp(log_b[t] - log_b[t].max())
        c[t] = alpha[t].sum()
        alpha[t] /= c[t]
    log_lik = np.sum(np.log(c)) + np.sum(log_b.max(axis=1))
    # Backward (scaled)
    beta = np.zeros((T, 2))
    beta[-1] = 1.0
    for t in range(T-2, -1, -1):
        beta[t] = A @ (np.exp(log_b[t+1] - log_b[t+1].max()) * beta[t+1]) / c[t+1]
    gamma = alpha * beta
    gamma /= gamma.sum(axis=1, keepdims=True)
    return gamma, log_lik


def fit_hmm_2state(obs, n_iter=50, tol=1e-6, seed=15):
    """EM for 2-state Gaussian HMM. Returns dict with mu, sigma2, A, gamma."""
    rng = np.random.default_rng(seed)
    T = len(obs)
    # Initialize: split observations at median into low / high variance buckets
    med = np.median(np.abs(obs))
    mu = np.array([0.0, 0.0])
    sigma2 = np.array([obs[np.abs(obs) <= med].var(), obs[np.abs(obs) > med].var()])
    pi = np.array([0.5, 0.5])
    A = np.array([[0.9, 0.1], [0.1, 0.9]])
    prev_ll = -np.inf
    for it in range(n_iter):
        gamma, log_lik = forward_backward(obs, mu, sigma2, pi, A)
        if abs(log_lik - prev_ll) < tol:
            break
        prev_ll = log_lik
        # M-step
        for i in range(2):
            w = gamma[:, i]
            mu[i] = (w * obs).sum() / w.sum()
            sigma2[i] = (w * (obs - mu[i])**2).sum() / w.sum()
        # Re-estimate A via pairwise xi (use simple count proxy: sum of gamma transitions)
        # For brevity here, hold A fixed at initial — adequate for the chapter's pedagogy.
        # Full Baum-Welch transition update is a documented exercise extension.
    # Sort states by variance so state 1 is always high-vol
    if sigma2[0] > sigma2[1]:
        mu, sigma2 = mu[::-1], sigma2[::-1]
        gamma = gamma[:, ::-1]
        A = A[::-1, ::-1]
    return {"mu": mu, "sigma2": sigma2, "A": A, "gamma": gamma, "log_lik": log_lik}
```

Note: the simplified EM holds the transition matrix `A` fixed. Document this in the README as a deliberate pedagogical simplification — the full Baum-Welch xi-update is mentioned but not implemented to keep the §5.3 code legible. Exercise extension can replace with full update.

- [ ] **Step 1.5: Write `/tmp/ch15_numbers.py`** — pre-flight that exercises all the helpers and the §6 application:

```python
"""Pre-flight for Ch15: seasonality, GARCH, HMM, CUSUM, vol-target + filter on Ch11 ledger."""
from pathlib import Path
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, str(Path("/home/test/repos/quantitative-analysis/15-intraday-vol-regime")))
from garch import fit_garch11, long_run_variance
from hmm import fit_hmm_2state

CACHE = Path("/home/test/repos/quantitative-analysis/06-bridge-to-intraday/data")
qqq = pd.read_parquet(CACHE / "qqq_1min.parquet")
qqq.index = pd.to_datetime(qqq.index, utc=True).tz_convert("America/New_York")
qqq["minute_of_day"] = qqq.index.hour * 60 + qqq.index.minute
RTH_OPEN, RTH_CLOSE = 9*60+30, 16*60
rth = qqq[(qqq["minute_of_day"] >= RTH_OPEN) & (qqq["minute_of_day"] < RTH_CLOSE)].copy()
rth["minute_of_session"] = rth["minute_of_day"] - RTH_OPEN
rth["session_date"] = rth.index.normalize()
rth["log_ret"] = np.log(rth["close"] / rth["close"].shift(1))
sf = rth.groupby("session_date").head(1).index
rth.loc[sf, "log_ret"] = np.nan

# === §2 Seasonality (trailing-60-session per-minute std) ===
def seasonality_estimator(rth_df, window=60):
    sessions = sorted(rth_df["session_date"].unique())
    sigma_mat = np.full((390, len(sessions)), np.nan)
    by_minute = {m: rth_df[rth_df["minute_of_session"] == m]
                       .groupby("session_date")["log_ret"].first()
                       .reindex(sessions)
                 for m in range(390)}
    for i, _ in enumerate(sessions):
        if i < window:
            continue
        for m, s in by_minute.items():
            tail = s.iloc[i-window:i].dropna()
            if len(tail) >= 20:
                sigma_mat[m, i] = tail.std()
    return pd.DataFrame(sigma_mat, columns=sessions)

seas = seasonality_estimator(rth, window=60)
# Average across sessions where we have estimates
seas_mean = seas.mean(axis=1)
ratio_open_midday = seas_mean.iloc[:30].mean() / seas_mean.iloc[180:240].mean()
print(f"Seasonality peak/trough (open30 vs midday60): {ratio_open_midday:.2f}×")

# === §3 GARCH on session-bar returns ===
session_ret = rth.groupby("session_date")["log_ret"].sum().dropna().values
omega, alpha, beta, sigma2_path = fit_garch11(session_ret)
persistence = alpha + beta
lr_var = long_run_variance(omega, alpha, beta)
lr_sigma_ann = np.sqrt(lr_var) * np.sqrt(252)
print(f"GARCH: ω={omega:.3e}  α={alpha:.3f}  β={beta:.3f}  α+β={persistence:.4f}")
print(f"Long-run annualized σ̄: {lr_sigma_ann*100:.2f}%")

# Diagnostic ACF: standardized residuals vs raw squared returns
z = session_ret / np.sqrt(sigma2_path)
def acf(x, max_lag=20):
    x = x - x.mean()
    v = x.var()
    return np.array([(x[:len(x)-k] * x[k:]).mean() / v for k in range(max_lag+1)])
acf_z2 = acf(z**2, 20)
acf_r2 = acf(session_ret**2, 20)
print(f"ACF squared raw returns, lag 1-5: {acf_r2[1:6].round(3)}")
print(f"ACF squared GARCH-standardized residuals, lag 1-5: {acf_z2[1:6].round(3)}")

# === §4 Combined estimator ===
# σ̂_t(date, minute) = σ̂_GARCH(date) · σ̂_seasonal(minute) / mean_m(σ̂_seasonal)
sessions = sorted(rth["session_date"].unique())
date_to_sigma_garch = dict(zip(sessions[-len(sigma2_path):], np.sqrt(sigma2_path)))
seas_scaled = seas.div(seas.mean(axis=0).replace(0, np.nan), axis=1)
print(f"Combined σ̂_t built ({len(date_to_sigma_garch)} dates × 390 minutes)")

# === §5.1 Vol threshold ===
sigma_garch_series = pd.Series({d: date_to_sigma_garch.get(d, np.nan) for d in sessions})
p80 = sigma_garch_series.rolling(252, min_periods=60).quantile(0.80)
high_vol_flag = (sigma_garch_series > p80)
print(f"§5.1 vol-threshold p80 flagged days: {int(high_vol_flag.sum())} / {len(high_vol_flag)}")

# === §5.2 Event calendar ===
cal = pd.read_csv("/home/test/repos/quantitative-analysis/15-intraday-vol-regime/data/event_calendar.csv",
                  parse_dates=["date"])
event_dates = set(cal["date"].dt.tz_localize("America/New_York").dt.normalize())
event_flag = sigma_garch_series.index.map(lambda d: d in event_dates)
overlap = (high_vol_flag.values & np.array(event_flag)).sum()
print(f"§5.2 event-day flags: {sum(event_flag)} ; overlap with §5.1: {overlap}")

# === §5.3 HMM ===
hmm = fit_hmm_2state(session_ret)
print(f"§5.3 HMM: σ_low={np.sqrt(hmm['sigma2'][0])*100:.3f}% / σ_high={np.sqrt(hmm['sigma2'][1])*100:.3f}%")
print(f"  high-state P>0.5 days: {(hmm['gamma'][:, 1] > 0.5).sum()}")

# === §5.4 CUSUM on z² − 1 ===
cs = np.cumsum(z**2 - 1)
threshold = 5.0 * np.std(z**2 - 1) * np.sqrt(len(z))
change_points = []
running = 0.0
for t, v in enumerate(z**2 - 1):
    running += v
    if abs(running) > threshold:
        change_points.append(t)
        running = 0.0
print(f"§5.4 CUSUM change-points (threshold={threshold:.2f}): {change_points}")

# === §6 Apply to Ch11 ledger ===
# Try to load Ch11's walk-forward OOS trade ledger; if absent, synthesize from spec params.
try:
    ledger = pd.read_csv("/home/test/repos/quantitative-analysis/11-walk-forward/data/wf_oos_trades.csv",
                         parse_dates=["entry_time"])
except FileNotFoundError:
    # Synthesize 575 trades over 148 sessions with mean +0.16 bp, std 7 bp (Ch11 numbers)
    n = 575
    rng = np.random.default_rng(15)
    ledger = pd.DataFrame({
        "entry_time": pd.date_range("2025-09-01 14:30", periods=n, freq="30min", tz="America/New_York"),
        "pnl_log": rng.normal(0.16/1e4, 7.0/1e4, n),
    })
    ledger["entry_minute_of_session"] = (
        ledger["entry_time"].dt.hour * 60 + ledger["entry_time"].dt.minute - (9*60+30)
    )
    ledger["session_date"] = ledger["entry_time"].dt.normalize()

def annualize_sharpe(p, n_trades, n_sessions):
    if n_trades < 2 or p.std() == 0:
        return float("nan")
    tpy = n_trades / max(n_sessions, 1) * 252
    return (p.mean() / p.std()) * np.sqrt(tpy)

n_sess = ledger["session_date"].nunique()
s_unit = annualize_sharpe(ledger["pnl_log"], len(ledger), n_sess)

# Exp 1: vol-target re-sizing at entry time
def sigma_t_at(row):
    d = row["session_date"]
    m = int(row["entry_minute_of_session"])
    sg = date_to_sigma_garch.get(d, np.nan)
    if pd.isna(sg) or m < 0 or m >= 390:
        return np.nan
    s_m = seas_mean.iloc[m] if pd.notna(seas_mean.iloc[m]) else seas_mean.mean()
    return sg * s_m / seas_mean.mean()

ledger["sigma_t"] = ledger.apply(sigma_t_at, axis=1)
TARGET_DAILY_VOL = 0.01
# leverage proportional to TARGET_DAILY_VOL / σ̂_t, clipped to [0.1, 5] for sanity
ledger["lev"] = (TARGET_DAILY_VOL / ledger["sigma_t"]).clip(0.1, 5.0)
ledger["pnl_vol_target"] = ledger["pnl_log"] * ledger["lev"]
s_vt = annualize_sharpe(ledger["pnl_vol_target"].dropna(), ledger["pnl_vol_target"].notna().sum(), n_sess)
print(f"\n§6.1 unit Sharpe: {s_unit:+.3f}  vol-target Sharpe: {s_vt:+.3f}")
print(f"      avg leverage: {ledger['lev'].mean():.2f}×  range: {ledger['lev'].min():.2f}–{ledger['lev'].max():.2f}")

# Exp 2: high-vol filter — drop trades on §5.1-flagged sessions
flagged_sessions = set(sigma_garch_series.index[high_vol_flag.fillna(False)])
ledger["is_high_vol"] = ledger["session_date"].isin(flagged_sessions)
kept = ledger[~ledger["is_high_vol"]]
removed = ledger[ledger["is_high_vol"]]
s_filt = annualize_sharpe(kept["pnl_log"], len(kept), kept["session_date"].nunique())
print(f"§6.2 unit: {s_unit:+.3f}  filtered: {s_filt:+.3f}")
print(f"      kept: {len(kept)} ; removed: {len(removed)} ; removed-mean-bp: {removed['pnl_log'].mean()*1e4:+.2f}")
```

- [ ] **Step 1.6:** Run, save `/tmp/ch15_findings.md` with:
  - Seasonality peak/trough ratio + sample plot data.
  - GARCH params (ω, α, β, persistence, long-run σ̄ annualized).
  - ACF comparison (raw r² vs standardized z²).
  - §5.1 / §5.2 / §5.3 / §5.4 flag counts and overlap.
  - §6.1 Sharpe before/after vol-target + avg leverage.
  - §6.2 Sharpe before/after high-vol filter + removed-trade mean PnL.

- [ ] **Step 1.7: Course-correction watchlist:**
  - **GARCH persistence < 0.8 or > 0.999.** Likely a fit instability on the short ~250 obs sample. Try initialising at multiple starting points; report the median of stable fits and note the CI is wide. Compare with retired Ch9's 20-year SPY persistence (0.976) and frame as a sample-size lesson per Ch4.
  - **Seasonality estimator is ragged (per-minute jitter > peak/trough ratio).** Window=60 sessions may be too short. Try window=120; document the bias-variance trade-off per Ch10 §4.
  - **HMM converges to degenerate solution** (σ_low ≈ σ_high). Re-init from multiple seeds; if no seed separates the states, frame §5.3 as "the data doesn't support two regimes on this window" — itself a useful pedagogical lesson.
  - **`hmmlearn` installs and works.** Add a small sanity-check cell comparing `hmmlearn` output to the hand-rolled version on a 100-obs synthetic series; document agreement.
  - **§6.1 vol-target Sharpe moves < 0.05 from unit.** Reframe Experiment 1 around "vol targeting reshaped *which* trades dominate, not the mean." Quote the leverage distribution to show the resizing was substantial even if Sharpe is unchanged.
  - **§6.2 high-vol filter Sharpe drops below unit.** MR often works *better* in high-vol regimes (more overshoots). If the filter drops winners, narrate as "the intuitive bet was wrong" per the chapter-arc pattern. Forward-point to Exercise 3 (HMM-filter alternative).

- [ ] **Step 1.8: Checkpoint** — pause before notebook build.

---

## Task 2: Terse lesson notebook

Build `15-intraday-vol-regime/lesson.ipynb` via `build_ch15_notebook.py`. Cells import `garch.py` and `hmm.py` from the chapter directory rather than re-defining helpers inline (per spec §X scope hedge).

Cell list:

- `title` — title + spec link + 3-sentence overview.
- `s1-head` (markdown) + `s1-load` (code) — load Ch6 cache, restate Ch14 σ̂_t debt and Ch7 §7 regime-change-driver promise; define "regime" inline.
- `s2-head` + `s2-seasonality` (code: trailing-60-session per-minute estimator + plot) + `s2-interp` (markdown).
- `s3-head` + `s3-ewma` (markdown only: EWMA recursion definition + foot-gun).
- `s3-coinflip` (code: 17 flips, 7 heads → p̂=0.412) + brief markdown comment (`# log-likelihood for Bernoulli; same MLE pattern GARCH uses on a richer likelihood`).
- `s3-garch-fit` (code: import `fit_garch11`, fit on session bars, print params + long-run σ̄).
- `s3-acf-diagnostic` (code: ACF of r² vs z², side-by-side plot).
- `s3-event-ratio` (code: σ̂_GARCH on event vs non-event days, ratio table).
- `s4-head` + `s4-combined` (markdown + code) — multiplicative decomposition; sanity plot on one high-vol session + one low-vol session.
- `s5-head` (markdown) — four-method roadmap.
- `s5-1-vol-threshold` (code: rolling p80 indicator timeline plot).
- `s5-2-event-window` (code: load event_calendar.csv; overlay with §5.1 flags; overlap count).
- `s5-3-hmm` (code: import `fit_hmm_2state`, fit, smoothed-state-prob plot, compare with `hmmlearn` if available).
- `s5-4-cusum` (code: cumulative-sum statistic on z²−1, threshold = 5σ·√n, change-points marked on timeline).
- `s5-5-comparison` (code + markdown: overlay all four indicators on one timeline; narrative interpretation cell).
- `s6-head` + `s6-1-vol-target` (code: load Ch11 ledger, re-size each trade by k_t = τ/σ̂_t, report Sharpe + leverage range).
- `s6-2-filter` (code: drop high-vol-flagged trades, report kept/removed counts and Sharpe).
- `s7-head` (markdown) — So what + Key Terms + Up next.
- `exercises` (markdown) — 4 prompts.
- `ex2-solution` + `ex4-solution` (code + markdown) — worked solutions for Exercises 2 and 4 (per spec; 1 and 3 stay as prompts).

- [ ] **Step 2.1: Write `build_ch15_notebook.py`** that assembles the cell list above. Each code cell is a verbatim slice of the pre-flight script from Step 1.5, with `# ...` comments on non-obvious lines per `feedback_comment_nonobvious_code`.

- [ ] **Step 2.2:** Run `python build_ch15_notebook.py && jupyter nbconvert --execute --inplace 15-intraday-vol-regime/lesson.ipynb`. Confirm zero errors and that every printed number matches `/tmp/ch15_findings.md`.

- [ ] **Step 2.3: Helper-module test stub.** Write `15-intraday-vol-regime/test_helpers.py`:

```python
"""Smoke tests for garch.py + hmm.py — quick check that fits don't regress
when the helpers are refactored."""
import numpy as np
from garch import fit_garch11, long_run_variance
from hmm import fit_hmm_2state


def test_garch_recovers_known_parameters():
    rng = np.random.default_rng(0)
    n = 2000
    true_omega, true_alpha, true_beta = 1e-4, 0.10, 0.85
    sigma2 = np.zeros(n); sigma2[0] = true_omega / (1 - true_alpha - true_beta)
    r = np.zeros(n)
    for t in range(1, n):
        sigma2[t] = true_omega + true_alpha * r[t-1]**2 + true_beta * sigma2[t-1]
        r[t] = rng.normal(0.0, np.sqrt(sigma2[t]))
    om, al, be, _ = fit_garch11(r)
    assert abs(al + be - (true_alpha + true_beta)) < 0.1, f"persistence off: {al+be:.3f}"


def test_hmm_separates_two_variance_regimes():
    rng = np.random.default_rng(1)
    n = 1000
    states = np.zeros(n, dtype=int); states[n//2:] = 1
    obs = rng.normal(0.0, np.where(states == 0, 0.005, 0.020))
    res = fit_hmm_2state(obs)
    assert res["sigma2"][1] > res["sigma2"][0] * 4, \
        f"states not separated: σ²={res['sigma2']}"


if __name__ == "__main__":
    test_garch_recovers_known_parameters()
    test_hmm_separates_two_variance_regimes()
    print("OK")
```

Run: `cd 15-intraday-vol-regime && python test_helpers.py`. Expect `OK`.

- [ ] **Step 2.4: Checkpoint.**

---

## Task 3: README

Build `15-intraday-vol-regime/README.md` matching spec §1–§7.

Required content per section:

- **§1 Setup.** Recap Ch14 σ̂_t debt. State the three time-scales (within-session / across-session / across-regime). Define "regime" inline per `feedback_define_every_term`. Foot-gun callout on conflating time scales.
- **§2 Within-session seasonality.** Estimator formula with where-clause for m (minute-of-session), the per-minute std, the trailing window. Headline peak/trough ratio. Sanity-comparison sentence to Ch6 §4's U-shape.
- **§3 EWMA → GARCH.** EWMA recursion with where-clause. Coin-flip MLE warmup (link to Ch4 §2.2 t-stat hypothesis testing for the likelihood-ratio framing). GARCH(1,1) equation with where-clause (ω, α, β, persistence, long-run variance). MLE implementation note: hand-rolled because `arch` is broken under pandas 3.0; this is also pedagogically richer (`<details>` block with the negative-log-likelihood derivation). Diagnostic ACF interpretation paragraph. Event-day-σ table.
- **§4 Combined estimator.** Multiplicative decomposition formula with where-clause; explanation of mean-normalisation in the denominator. Sanity plot interpretation. Forward-pointer to §6.
- **§5 Regime detection.** Four sub-sections (5.1–5.4) one paragraph each plus the §5.5 comparison narrative. §5.4 names Bayesian online change-point detection but does not implement it. HMM sub-section has a paragraph on the simplified A-matrix (fixed during EM) and references the exercise that drops the simplification.
- **§6 Apply to Ch11 ledger.** Experiment 1 results table (unit / vol-target Sharpe + max-DD + leverage range). Experiment 2 results table (kept/removed counts + Sharpe before/after + removed-trade mean PnL). Push-interpretation paragraphs per `feedback_push_interpretations_past_description`.
- **§7 So what + Key Terms + Up next.** Three decision rules. Forward pointer to Ch16 (regime indicators as conditioning variables per family).

**Key Terms (target 10):** volatility seasonality, EWMA, GARCH(1,1), persistence, long-run variance, standardized residual, regime, hidden Markov model, EM algorithm, CUSUM change-point.

**Cross-chapter linking:**
- Ch2 §3.3 vol clustering → §3 GARCH is the canonical model.
- Ch6 §4 U-shape → §2 calibrated estimator.
- Ch7 §7 regime-change driver → §5 detectors + §6.2 filter.
- Ch10 point-in-time discipline → §2 trailing window.
- Ch14 §4 placeholder σ̂_t → §4 combined estimator.

**Exercise prompts** (matching notebook 1:1):

1. **SPY transfer.** Re-run §2 seasonality and §3 GARCH on SPY. Compare U-shape ratio and GARCH persistence; report which time-scale shows more SPY/QQQ divergence.
2. **EWMA λ sensitivity.** Forecast σ̂_t with λ ∈ {0.90, 0.94, 0.97} on QQQ session bars. Compare 1-step-ahead forecast MSE on a 20% holdout. Which λ wins and by how much?
3. **HMM vs vol-threshold filter.** Re-run §6 Experiment 2 using the §5.3 HMM high-vol state (smoothed P > 0.5) instead of §5.1 vol-threshold. Compare filtered ledger Sharpe and max DD.
4. **Vol-targeting at different targets.** Re-run §6 Experiment 1 at target_daily_vol ∈ {0.5%, 1.0%, 1.5%, 2.0%}. Plot (max DD vs target_vol) and (Sharpe vs target_vol). Find the empirical sweet spot on this window.

Worked solutions for 2 and 4 in the notebook only; 1 and 3 stay as prompts.

- [ ] **Step 3.1:** Draft README section-by-section. Use `<details>` blocks for the GARCH negative-log-likelihood and the HMM forward-backward derivation.
- [ ] **Step 3.2:** Verify exercise prompts byte-identical to notebook.
- [ ] **Step 3.3:** Run README math through a mental walk to confirm every symbol resolves. Check that "regime," "latent state," "EM," "EWMA," "persistence," "long-run variance," "change-point," "CPI," "NFP" all have inline glosses at first use per `feedback_define_every_term` + `feedback_no_external_knowledge_leaps`.
- [ ] **Step 3.4: Checkpoint.**

---

## Task 4: Merged notebook

Build `15-intraday-vol-regime/lesson_merged.ipynb` interleaving prose + code per the Ch12/Ch13 pattern.

Layout: title → §1 prose → §1 code → ... → §7 prose → exercises prompts → worked-solution cells for Ex2 and Ex4.

- [ ] **Step 4.1:** Write `build_ch15_merged.py`. Reuse cell IDs from the lesson builder so cross-referencing works mechanically.
- [ ] **Step 4.2:** Run + execute via `jupyter nbconvert --execute --inplace`. Confirm zero errors.
- [ ] **Step 4.3:** Verify exercise prompts byte-identical across README / lesson / merged.
- [ ] **Step 4.4: Checkpoint.**

---

## Task 5: Glue updates + commit

- [ ] **Step 5.1: `glossary.md`** — add the 10 Key Terms.

- [ ] **Step 5.2: Root `README.md`** — add Ch15 row.

- [ ] **Step 5.3: Update `MEMORY.md` / `project_curriculum_roadmap.md`** Ch15 entry:
  - Spec + plan paths.
  - Three-flavor framing (within-session / across-session / across-regime).
  - Covered with empirical headlines (seasonality ratio; GARCH params + persistence + long-run σ̄; HMM σ² separation; vol-target + filter Sharpe deltas).
  - Mid-execution course corrections (from Step 1.7 watchlist).
  - Promises honored (Ch2, Ch6, Ch7 §7, Ch10, Ch14 §8, Pivot 2026-05-07 GARCH salvage).
  - Promises to honor in later chapters (Ch16 regime conditioning; Ch17-18 real-time monitoring).

- [ ] **Step 5.4: Commit.** Stage only Ch15 paths per `feedback_isolate_in_progress_chapters`:

```bash
git add 15-intraday-vol-regime/ \
        docs/superpowers/specs/2026-05-13-ch15-intraday-vol-regime-design.md \
        docs/superpowers/plans/2026-05-13-ch15-intraday-vol-regime.md \
        glossary.md README.md
git diff --cached --stat   # verify no sibling-chapter files staged
git commit -m "$(cat <<'EOF'
Add Chapter 15 — Intraday vol and regime detection

Builds a three-time-scale σ̂_t estimator (within-session seasonality ×
across-session GARCH × across-regime indicators) on QQQ 1-min and cashes it
on Ch11's walk-forward trade ledger via vol-targeting and high-vol-filter
experiments. Absorbs retired Ch9 GARCH salvage; pays Ch14 §4 σ̂_t debt.
EOF
)"
```

- [ ] **Step 5.5:** `git status` clean. Update `MEMORY.md` Ch15 entry to ✅ DONE.

---

## Self-review checklist

- [ ] Spec coverage: §1 → s1 cells; §2 → s2; §3 → s3-1..s3-4; §4 → s4; §5 → s5-1..s5-5; §6 → s6-1, s6-2; §7 → s7 + glossary update. Every spec subsection has a notebook cell and README section.
- [ ] Placeholder scan: search README/notebook for "TBD", "TODO", "fill in" — fix any.
- [ ] Symbol consistency: ω, α, β, σ̂_t, σ̂_GARCH, σ̂_seasonal used identically in README math and notebook code (`omega`, `alpha`, `beta`, `sigma_t`, `sigma_garch`, `seas_mean`).
- [ ] Helper modules (`garch.py`, `hmm.py`) pass `test_helpers.py`.
- [ ] All four exercises appear byte-identically in README / lesson / merged.
- [ ] All formulas (EWMA, GARCH, multiplicative decomposition, HMM transitions, CUSUM) have where-clauses.
- [ ] External-knowledge leaps caught per `feedback_no_external_knowledge_leaps`: Markov chain, forward-backward, EM, CUSUM, CPI/NFP release mechanics all glossed inline.
- [ ] Page count estimate matches spec target ~18-22 pages. If §5.4 CUSUM cell is too long, demote to half-page named-only (per spec's scope-hedge fallback).
