# Chapter 16 Implementation Plan — More Strategies: Momentum, Breakout, Event-Driven

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Chapter 16 — paired notebook + README — that runs the other three Ch7 strategy families (momentum, breakout, event-driven) through the same Ch9-13 honest-pipeline that deflated MR, produces a cross-family side-by-side deflation table, applies Ch15 regime indicators as conditioning variables, and picks the Ch17-18 paper-trade candidate (with explicit "all three outcomes pre-written" honesty about what verdict the data may produce).

**Architecture:** `16-more-strategies/`. Reuses Ch6 QQQ 1-min parquet, Ch15 σ̂_t combined estimator (`garch.py`, `hmm.py`, `event_calendar.csv` imported from Ch15), Ch12 cost stack, Ch13 toxicity diagnostic, Ch9 event-driven loop. No new external data. The chapter is large; per spec, each family lives in its own notebook section with the same 6-step sub-structure (signal → backtest → cost-aware k\* → execution → regime conditioning → verdict) and §5 is the cross-family synthesis.

**Tech Stack:** Python 3.11+, pandas, numpy, scipy, matplotlib. No new deps.

**Spec reference:** `docs/superpowers/specs/2026-05-13-ch16-more-strategies-design.md`

**Honest-data working targets:**

| Family | Stage | Working Target | Notes |
|---|---|---|---|
| Momentum | lag-k ρ at k ∈ {1, 5, 30, 60, 120, 240, 390} | mostly near zero; max |ρ| at k=120 ≈ +0.004 | inherits Ch7 §6 |
| Momentum | In-sample Sharpe (no cost) | −0.5 to +1.5 | tiny signal; high variance |
| Momentum | Cost-aware Sharpe at k\* | −2.0 to 0.0 | likely fails the Ch12 bar |
| Momentum | Maker fill rate (Ch13 sim) | < 30% | signal IS the move ⇒ low fill |
| Breakout-confirm | trades/year | 200–500 | one entry per session per direction |
| Breakout-confirm | Cost-aware Sharpe | −1.5 to +1.0 | borderline candidate |
| Breakout-anticipate | fill rate | 60–90% | stop-limit at OR_high+ε |
| Breakout-anticipate | toxicity from Ch13 formula | 0.5–3.0 bp | false-break penalty |
| Event-driven | trade count | ≤ 16 | 8 FOMC sessions × 2 hypotheses |
| Event-driven | CI half-width | ±2.5 or wider | sample-size honesty |
| Cross-family | best post-cost Sharpe | could be negative | all-three-outcomes pre-written |

**Computational sanity:** Three event-driven backtests × ~250 sessions = 3× Ch9 cost. Regime conditioning re-runs each backtest under 4 regime stratifications = 12× Ch9 cost ≈ 30s. ORB 2D sweep (3 percentile buckets × 3 ε values × 2 variants) is the heaviest piece — should still run < 60s.

---

## File map

| File | Status |
| --- | --- |
| `16-more-strategies/lesson.ipynb` | create |
| `16-more-strategies/lesson_merged.ipynb` | create |
| `16-more-strategies/README.md` | create |
| `16-more-strategies/pipeline.py` | create (shared event-driven loop + cost stack + toxicity helpers) |
| `16-more-strategies/momentum.py` | create (signal + backtest specialization) |
| `16-more-strategies/breakout.py` | create (ORB signal + both execution variants) |
| `16-more-strategies/event_driven.py` | create (FOMC pre/post-window signal) |
| `glossary.md` | modify |
| `README.md` (root) | modify |
| Memory roadmap | modify |

The four helper modules keep each notebook cell short. They reuse code from Ch9 (event-driven loop), Ch12 (cost stack), Ch13 (toxicity), Ch15 (σ̂_t + regime indicators). Where pre-existing chapter code is reused, prefer `from pathlib import Path; sys.path.insert(...)` + module imports over copy-paste; if a chapter doesn't expose a clean module, copy the relevant ~30-line function into `pipeline.py` and cite the source chapter in a docstring.

---

## Task 1: Helper modules + pre-flight

This task is sized larger than Ch12-15 Task 1 because three families share a pipeline. Build the pipeline once, then exercise it three times.

- [ ] **Step 1.1:** Create the chapter directory.

```bash
mkdir -p 16-more-strategies
```

- [ ] **Step 1.2: Write `16-more-strategies/pipeline.py`** — the shared backtest + cost + toxicity engine.

```python
"""Shared pipeline for Ch16 strategy families.

Reuses the Ch9 single-position event-driven loop with strategy-specific
signal and exit hooks. Cost stack is Ch12's (Roll's spread + IBKR commission +
square-root impact). Toxicity diagnostic is Ch13's (drift_uncond − drift_filled).
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
import numpy as np
import pandas as pd

CACHE = Path("/home/test/repos/quantitative-analysis/06-bridge-to-intraday/data")


def load_qqq_1min():
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
    return rth


@dataclass
class Trade:
    session_date: pd.Timestamp
    entry_minute: int
    exit_minute: int
    direction: int   # +1 long, -1 short
    entry_px: float
    exit_px: float
    pnl_log: float

    @property
    def pnl_bp(self) -> float:
        return self.pnl_log * 1e4


@dataclass
class Strategy:
    """Specialization point: each family provides these callbacks.

    signal_fn(day_df, prior_state) -> (signal, K_max) or None
        Called once per bar (or once per session for breakout) on the session's
        bar DataFrame.  signal ∈ {-1, 0, +1}, K_max is the max-hold in bars.
        prior_state is a chapter-specific dict (e.g., {"opening_range": (lo, hi)}).
    state_init(day_df) -> dict
        Called once at session start to compute strategy-specific state.
    """
    name: str
    signal_fn: Callable
    state_init: Callable = field(default=lambda day: {})


def event_driven_backtest(rth: pd.DataFrame, strategy: Strategy,
                          K_default: int = 3) -> pd.DataFrame:
    """Single-position event-driven loop. Inherits Ch9 §2 conventions:
       exit-before-entry order; force-flatten at last bar of session."""
    trades = []
    for date, day in rth.groupby("session_date"):
        day = day.sort_index().reset_index()
        state = strategy.state_init(day)
        in_pos = 0
        entry_i, entry_px, K_remaining = None, None, None
        direction = 0
        for i in range(len(day)):
            # Exit first
            if in_pos != 0 and (K_remaining is not None and i - entry_i >= K_remaining):
                exit_i = min(i, len(day) - 1)
                exit_px = day.loc[exit_i, "open"] if i < len(day) else day.loc[exit_i, "close"]
                trades.append(Trade(
                    session_date=date, entry_minute=int(day.loc[entry_i, "minute_of_session"]),
                    exit_minute=int(day.loc[exit_i, "minute_of_session"]),
                    direction=direction, entry_px=entry_px, exit_px=exit_px,
                    pnl_log=direction * np.log(exit_px / entry_px),
                ))
                in_pos = 0; entry_i = None; entry_px = None
            # Entry
            if in_pos == 0:
                result = strategy.signal_fn(day, i, state)
                if result is not None:
                    sig, K = result
                    if sig != 0 and i + 1 < len(day):
                        in_pos = 1; direction = sig
                        entry_i = i + 1
                        entry_px = day.loc[entry_i, "open"]
                        K_remaining = K
        # Force flatten at session end
        if in_pos != 0 and entry_i is not None:
            exit_i = len(day) - 1
            trades.append(Trade(
                session_date=date, entry_minute=int(day.loc[entry_i, "minute_of_session"]),
                exit_minute=int(day.loc[exit_i, "minute_of_session"]),
                direction=direction, entry_px=entry_px, exit_px=day.loc[exit_i, "close"],
                pnl_log=direction * np.log(day.loc[exit_i, "close"] / entry_px),
            ))
    return pd.DataFrame([t.__dict__ for t in trades])


# === Cost stack (Ch12) ===
ROLL_HALF_SPREAD_BP = 0.72         # from Ch12 finding
COMMISSION_BP_PER_LEG = 0.07       # IBKR tiered, $30k Q
IMPACT_ETA = 0.10                  # square-root impact coefficient
DAILY_SIGMA = 0.0102               # QQQ daily σ (from Ch12)
ADV_USD = 15e9                     # consolidated ADV


def round_trip_cost_bp(q_usd: float = 30_000) -> float:
    """Return round-trip cost in bp for a market-order strategy at notional q.
    Spread (paid twice) + commission (twice) + impact (twice)."""
    spread = 2 * ROLL_HALF_SPREAD_BP
    commission = 2 * COMMISSION_BP_PER_LEG
    impact_one_leg = IMPACT_ETA * DAILY_SIGMA * np.sqrt(q_usd / ADV_USD) * 1e4
    return spread + commission + 2 * impact_one_leg


# === Sharpe annualization (Ch9 §4) ===
def annualize_sharpe(pnl: pd.Series, n_sessions: int) -> float:
    if len(pnl) < 2 or pnl.std() == 0:
        return float("nan")
    tpy = len(pnl) / max(n_sessions, 1) * 252
    return (pnl.mean() / pnl.std()) * np.sqrt(tpy)


# === Toxicity (Ch13) ===
def toxicity_bp(filled_pnl: pd.Series, unconditional_pnl: pd.Series) -> float:
    """drift_uncond − drift_filled, in bp."""
    return (unconditional_pnl.mean() - filled_pnl.mean()) * 1e4
```

- [ ] **Step 1.3: Write `16-more-strategies/momentum.py`**

```python
"""Trailing N-min momentum on QQQ. Mirror of Ch8's MR with sign flipped.
Empirical hook: Ch7 §6 lag-120 ρ = +0.004."""
import numpy as np
import pandas as pd
from pipeline import Strategy


def momentum_lag_sweep(rth: pd.DataFrame, lags=(1, 5, 30, 60, 120, 240, 390)):
    """Compute lag-k autocorrelation of 1-min log returns within sessions only.
    Returns {lag: rho}."""
    out = {}
    for k in lags:
        # Per-session lag, then average
        rhos = []
        for _, day in rth.groupby("session_date"):
            r = day["log_ret"].dropna().values
            if len(r) > k + 1:
                rhos.append(np.corrcoef(r[k:], r[:-k])[0, 1])
        out[k] = float(np.nanmean(rhos))
    return out


def make_momentum_strategy(N: int, K: int, k_sigma: float,
                           sigma_t_lookup) -> Strategy:
    """N-min trailing momentum; entry when |r_{t,t-N}| > k_σ · σ̂_t · √(N/60); hold K."""
    def state_init(day):
        return {"N": N, "K": K, "k_sigma": k_sigma}

    def signal_fn(day, i, state):
        N_, K_, ks = state["N"], state["K"], state["k_sigma"]
        if i < N_:
            return None
        mos = int(day.loc[i, "minute_of_session"])
        if mos + K_ >= 390:    # leave room to flatten before close
            return None
        prior = np.log(day.loc[i, "close"] / day.loc[i-N_, "close"])
        s = sigma_t_lookup(day.loc[i, "session_date"], mos)
        if np.isnan(s) or s <= 0:
            return None
        threshold = ks * s * np.sqrt(N_ / 60.0)
        if prior > threshold:
            return (+1, K_)       # buy continuation
        elif prior < -threshold:
            return (-1, K_)       # sell continuation
        return None

    return Strategy(name=f"Momentum N={N} K={K} k={k_sigma}",
                    signal_fn=signal_fn, state_init=state_init)
```

- [ ] **Step 1.4: Write `16-more-strategies/breakout.py`**

```python
"""Opening Range Breakout (ORB) on QQQ.

OR_t = [low, high] of the first 30 minutes (minutes 0-29 of session t).
Two execution variants:
  - confirmation: enter at close of the 1-min bar where break confirmed (takes).
  - anticipation: stop-limit at OR_high + ε bp (long) / OR_low − ε bp (short) (makes).
"""
import numpy as np
import pandas as pd
from pipeline import Strategy

OR_WINDOW = 30   # minutes; Exercise 2 sweeps over {15, 30, 60}


def opening_range(day, window=OR_WINDOW):
    head = day[day["minute_of_session"] < window]
    if len(head) == 0:
        return (np.nan, np.nan)
    return (head["low"].min(), head["high"].max())


def make_breakout_confirmation(eps_bp: float = 0.0) -> Strategy:
    """Confirmation variant: enter on close of breaking bar."""
    def state_init(day):
        lo, hi = opening_range(day)
        return {"or_low": lo, "or_high": hi, "fired": False}

    def signal_fn(day, i, state):
        if state["fired"] or np.isnan(state["or_low"]):
            return None
        mos = int(day.loc[i, "minute_of_session"])
        if mos < OR_WINDOW or mos >= 380:
            return None
        c = day.loc[i, "close"]
        upper = state["or_high"] * (1 + eps_bp / 1e4)
        lower = state["or_low"] * (1 - eps_bp / 1e4)
        if c > upper:
            state["fired"] = True
            return (+1, 390 - mos - 1)   # hold until session close
        elif c < lower:
            state["fired"] = True
            return (-1, 390 - mos - 1)
        return None

    return Strategy(name=f"Breakout-confirm ε={eps_bp}bp",
                    signal_fn=signal_fn, state_init=state_init)


def make_breakout_anticipation(eps_bp: float = 5.0) -> Strategy:
    """Anticipation variant: posts a stop-limit at OR_high + ε / OR_low − ε.
    For backtest purposes we approximate fills by checking whether any bar's
    H/L touches the trigger after OR window closes and before session end.
    Toxicity diagnostic (Ch13 §4) is the headline output of this variant."""
    def state_init(day):
        lo, hi = opening_range(day)
        return {"or_low": lo, "or_high": hi, "fired": False,
                "trigger_up": hi * (1 + eps_bp / 1e4) if not np.isnan(hi) else None,
                "trigger_dn": lo * (1 - eps_bp / 1e4) if not np.isnan(lo) else None}

    def signal_fn(day, i, state):
        if state["fired"] or state["trigger_up"] is None:
            return None
        mos = int(day.loc[i, "minute_of_session"])
        if mos < OR_WINDOW or mos >= 380:
            return None
        if day.loc[i, "high"] >= state["trigger_up"]:
            state["fired"] = True
            return (+1, 390 - mos - 1)
        if day.loc[i, "low"] <= state["trigger_dn"]:
            state["fired"] = True
            return (-1, 390 - mos - 1)
        return None

    return Strategy(name=f"Breakout-anticipate ε={eps_bp}bp",
                    signal_fn=signal_fn, state_init=state_init)
```

- [ ] **Step 1.5: Write `16-more-strategies/event_driven.py`**

```python
"""FOMC pre/post drift on QQQ.

Two hypotheses:
  - Pre-release drift (minutes 240-299) predicts release-window (300-329) direction.
  - Release-window (300-329) predicts post-window (330-389) direction.
"""
import numpy as np
import pandas as pd

PRE_LO, PRE_HI = 240, 299
REL_LO, REL_HI = 300, 329
POST_LO, POST_HI = 330, 389


def event_signal_table(rth: pd.DataFrame, event_dates: set) -> pd.DataFrame:
    """One row per FOMC session: pre / release / post window log-returns."""
    rows = []
    for date, day in rth.groupby("session_date"):
        if date not in event_dates:
            continue
        day = day.sort_index().reset_index()

        def window_ret(lo, hi):
            slot = day[(day["minute_of_session"] >= lo) & (day["minute_of_session"] <= hi)]
            if slot.empty:
                return np.nan
            return np.log(slot["close"].iloc[-1] / slot["close"].iloc[0])

        rows.append({
            "date": date,
            "pre": window_ret(PRE_LO, PRE_HI),
            "release": window_ret(REL_LO, REL_HI),
            "post": window_ret(POST_LO, POST_HI),
        })
    return pd.DataFrame(rows)


def event_driven_pnl(tab: pd.DataFrame) -> pd.DataFrame:
    """Two single-trade-per-FOMC-day hypotheses.
       H1: sign(pre)  predicts release  → trade release direction = sign(pre)
       H2: sign(release) predicts post   → trade post direction = sign(release)
    """
    tab = tab.copy()
    tab["h1_pnl_log"] = np.sign(tab["pre"]) * tab["release"]
    tab["h2_pnl_log"] = np.sign(tab["release"]) * tab["post"]
    return tab
```

- [ ] **Step 1.6: Write `/tmp/ch16_numbers.py`** — pre-flight using all four modules. This is the meatiest pre-flight in the curriculum so far; it runs each family end-to-end through the 5-step pipeline.

```python
"""Pre-flight for Ch16: run the three families through the Ch9-13 pipeline."""
from pathlib import Path
import numpy as np
import pandas as pd
import sys
ch16 = "/home/test/repos/quantitative-analysis/16-more-strategies"
ch15 = "/home/test/repos/quantitative-analysis/15-intraday-vol-regime"
for p in (ch16, ch15):
    sys.path.insert(0, p)
from pipeline import (load_qqq_1min, event_driven_backtest,
                      round_trip_cost_bp, annualize_sharpe, toxicity_bp)
from momentum import momentum_lag_sweep, make_momentum_strategy
from breakout import make_breakout_confirmation, make_breakout_anticipation
from event_driven import event_signal_table, event_driven_pnl
from garch import fit_garch11
# Reuse Ch15 seasonality + GARCH for σ̂_t lookup

rth = load_qqq_1min()
print(f"Loaded {len(rth)} RTH bars over {rth['session_date'].nunique()} sessions")

# ===== §2 Momentum =====
print("\n=== §2 Momentum ===")
lags = momentum_lag_sweep(rth)
print("Lag-k ρ:", {k: f"{v:+.5f}" for k, v in lags.items()})

# Pick (N, K) — working pick at largest positive |ρ| from sweep
best_k = max(lags, key=lambda k: lags[k])
N_mom, K_mom = best_k, max(best_k // 2, 3)
print(f"Working pick: (N={N_mom}, K={K_mom})")

# Build σ̂_t lookup (simplified: rolling 20-day std of 1-min returns; full
# Ch15 combined estimator wired in notebook)
sigma_by_date = rth.groupby("session_date")["log_ret"].std().rolling(20).mean()

def sigma_t_lookup(date, mos):
    return sigma_by_date.get(date, np.nan)

# Cost-aware k_σ sweep
rt_cost_bp = round_trip_cost_bp(30_000)
print(f"Round-trip cost: {rt_cost_bp:.2f} bp")

mom_results = []
for k_sigma in [0.5, 0.7, 1.0, 1.3, 1.5, 1.8, 2.1, 2.5]:
    strat = make_momentum_strategy(N_mom, K_mom, k_sigma, sigma_t_lookup)
    tr = event_driven_backtest(rth, strat)
    if len(tr) == 0:
        continue
    n_sess = tr["session_date"].nunique()
    s_pre = annualize_sharpe(tr["pnl_log"], n_sess)
    tr["pnl_post_cost"] = tr["pnl_log"] - rt_cost_bp / 1e4
    s_post = annualize_sharpe(tr["pnl_post_cost"], n_sess)
    mom_results.append({"k_sigma": k_sigma, "n": len(tr), "s_pre": s_pre, "s_post": s_post})
df_mom = pd.DataFrame(mom_results)
print(df_mom.to_string(index=False))

# ===== §3 Breakout =====
print("\n=== §3 Breakout ===")
# Confirmation
conf = make_breakout_confirmation(eps_bp=0.0)
tr_conf = event_driven_backtest(rth, conf)
n_sess_conf = tr_conf["session_date"].nunique()
s_conf_pre = annualize_sharpe(tr_conf["pnl_log"], n_sess_conf)
tr_conf["pnl_post_cost"] = tr_conf["pnl_log"] - rt_cost_bp / 1e4
s_conf_post = annualize_sharpe(tr_conf["pnl_post_cost"], n_sess_conf)
print(f"Breakout-confirm: {len(tr_conf)} trades, S_pre={s_conf_pre:+.3f}, S_post={s_conf_post:+.3f}")

# Anticipation
ant = make_breakout_anticipation(eps_bp=5.0)
tr_ant = event_driven_backtest(rth, ant)
n_sess_ant = tr_ant["session_date"].nunique()
s_ant_pre = annualize_sharpe(tr_ant["pnl_log"], n_sess_ant)
print(f"Breakout-anticipate (eps=5bp): {len(tr_ant)} trades, S_pre={s_ant_pre:+.3f}")
# Toxicity: filled-bucket pnl vs same-signal-no-eps pnl
ant0 = make_breakout_anticipation(eps_bp=0.0)
tr_ant0 = event_driven_backtest(rth, ant0)
tox_bp = toxicity_bp(tr_ant["pnl_log"], tr_ant0["pnl_log"])
print(f"  toxicity = drift_uncond − drift_filled = {tox_bp:+.3f} bp")

# 2D sweep over OR-percentile × eps
bp_results = []
for or_pctile in [25, 50, 75]:
    for eps in [0.0, 5.0, 10.0]:
        # For brevity in pre-flight: only run confirmation here; full sweep in notebook
        st = make_breakout_confirmation(eps_bp=eps)
        tr = event_driven_backtest(rth, st)
        # Filter trades whose session's OR-width falls below the pctile bucket
        or_widths = rth.groupby("session_date").apply(
            lambda d: (d[d["minute_of_session"] < 30]["high"].max()
                       - d[d["minute_of_session"] < 30]["low"].min())
                      / d[d["minute_of_session"] < 30]["close"].iloc[0] * 1e4
        )
        bucket_threshold = or_widths.quantile(or_pctile / 100.0)
        keep = tr["session_date"].map(or_widths) >= bucket_threshold
        sel = tr[keep]
        if len(sel) > 5:
            s_pre = annualize_sharpe(sel["pnl_log"], sel["session_date"].nunique())
            sel = sel.assign(pnl_post_cost=sel["pnl_log"] - rt_cost_bp / 1e4)
            s_post = annualize_sharpe(sel["pnl_post_cost"], sel["session_date"].nunique())
        else:
            s_pre = s_post = np.nan
        bp_results.append({"or_pctile": or_pctile, "eps": eps, "n": len(sel),
                           "s_pre": s_pre, "s_post": s_post})
print(pd.DataFrame(bp_results).to_string(index=False))

# ===== §4 Event-driven =====
print("\n=== §4 Event-driven (FOMC) ===")
cal = pd.read_csv(f"{ch15}/data/event_calendar.csv", parse_dates=["date"])
fomc_dates = set(
    cal[cal["event_type"] == "FOMC"]["date"].dt.tz_localize("America/New_York").dt.normalize()
)
tab = event_signal_table(rth, fomc_dates)
print(f"FOMC sessions found in window: {len(tab)}")
ev = event_driven_pnl(tab)
print(ev[["date", "pre", "release", "post", "h1_pnl_log", "h2_pnl_log"]].round(5).to_string(index=False))
for col in ("h1_pnl_log", "h2_pnl_log"):
    p = ev[col].dropna()
    if len(p) < 2:
        continue
    p_post = p - rt_cost_bp / 1e4
    s_pre = (p.mean() / p.std()) * np.sqrt(252) if p.std() > 0 else np.nan
    s_post = (p_post.mean() / p_post.std()) * np.sqrt(252) if p_post.std() > 0 else np.nan
    # Bootstrap CI on Sharpe (i.i.d., 1000 resamples)
    rng = np.random.default_rng(16)
    boot = []
    for _ in range(1000):
        s = rng.choice(p.values, size=len(p), replace=True)
        boot.append((s.mean() / s.std()) * np.sqrt(252) if s.std() > 0 else np.nan)
    lo, hi = np.nanquantile(boot, [0.025, 0.975])
    print(f"  {col}: n={len(p)}  S_pre={s_pre:+.3f}  S_post={s_post:+.3f}  CI=({lo:+.2f}, {hi:+.2f})")

# ===== §5 Cross-family table =====
print("\n=== §5 Cross-family deflation table ===")
print(f"{'Family':<28} {'IS Sharpe':>10} {'Cost-aware':>11} {'Verdict':>10}")
print(f"{'MR (Ch8-13)':<28} {'+2.08':>10} {'-1.11':>11} {'Fail':>10}")
print(f"{'Momentum (best k)':<28} {df_mom['s_pre'].max():>+10.3f} {df_mom['s_post'].max():>+11.3f} {'TBD':>10}")
print(f"{'Breakout-confirm':<28} {s_conf_pre:>+10.3f} {s_conf_post:>+11.3f} {'TBD':>10}")
print(f"{'Breakout-anticipate':<28} {s_ant_pre:>+10.3f} {'see toxicity':>11} {'TBD':>10}")
```

- [ ] **Step 1.7:** Run the pre-flight; save `/tmp/ch16_findings.md` with:
  - Momentum lag-k sweep table.
  - Momentum cost-aware k\* sweep (k_σ vs S_pre vs S_post).
  - Breakout-confirm + Breakout-anticipate trade counts, Sharpes.
  - Breakout-anticipate toxicity in bp.
  - ORB 2D sweep (or_pctile × eps) Sharpe table.
  - Event-driven 8-trade FOMC table + per-hypothesis bootstrap CI.
  - Cross-family verdict table (rows filled with actuals).

- [ ] **Step 1.8: Course-correction watchlist** — this is the chapter most likely to surprise (per spec §"Expected mid-execution course corrections" 1-6). Document any of these that fire:

1. **Momentum lag-k all near zero.** Reframe §2 around "signal-to-noise is so small the cost stack swamps it before optimization can find it." Headline shifts from "what threshold?" to "no threshold helps."
2. **ORB-confirm cost-aware Sharpe positive with CI not straddling zero too badly.** This is the chapter's positive-headline scenario. Write the §5.3 verdict carefully so "positive but small N" is the honest framing, not triumphalist.
3. **ORB-anticipate toxicity small (< 0.5 bp).** Reframe §3.5 around "directional bets get different toxicity than reversion bets" — pedagogically sharpens Ch13.
4. **Event-driven N=8 produces extreme point estimate** (|Sharpe| > 3). Stand firm on the sample-size honesty: the CI dwarfs the point estimate; don't read into it.
5. **Cross-family §5.3 verdict is "none survive."** All three pre-stated outcomes are in spec — pick the matching narrative.
6. **Regime-fingerprint heatmap §5.2 cells too noisy.** Demote from full heatmap to a single "best regime per family" sentence.

- [ ] **Step 1.9: Helper-module tests.** Write `16-more-strategies/test_helpers.py`:

```python
"""Smoke tests for pipeline.py + family modules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "15-intraday-vol-regime"))
import numpy as np
import pandas as pd
from pipeline import load_qqq_1min, event_driven_backtest, annualize_sharpe
from momentum import make_momentum_strategy
from breakout import make_breakout_confirmation


def test_event_driven_returns_dataframe_with_required_columns():
    rth = load_qqq_1min()
    sample = rth[rth["session_date"].isin(
        sorted(rth["session_date"].unique())[:5]
    )]
    sigma = sample["log_ret"].std()
    strat = make_momentum_strategy(N=5, K=3, k_sigma=1.0,
                                   sigma_t_lookup=lambda d, m: sigma)
    tr = event_driven_backtest(sample, strat)
    expected_cols = {"session_date", "entry_minute", "exit_minute",
                     "direction", "entry_px", "exit_px", "pnl_log"}
    assert expected_cols.issubset(set(tr.columns)), f"missing: {expected_cols - set(tr.columns)}"


def test_breakout_fires_at_most_once_per_session():
    rth = load_qqq_1min()
    sample = rth[rth["session_date"].isin(
        sorted(rth["session_date"].unique())[:20]
    )]
    strat = make_breakout_confirmation(eps_bp=0.0)
    tr = event_driven_backtest(sample, strat)
    per_session = tr.groupby("session_date").size()
    assert (per_session <= 1).all(), f"breakout fired multiple times: {per_session[per_session > 1]}"


if __name__ == "__main__":
    test_event_driven_returns_dataframe_with_required_columns()
    test_breakout_fires_at_most_once_per_session()
    print("OK")
```

Run: `cd 16-more-strategies && python test_helpers.py`. Expect `OK`.

- [ ] **Step 1.10: Checkpoint** — pause before notebook build. Pre-flight produced the numbers; confirm watchlist items before commitment to the spec's three-family structure.

---

## Task 2: Terse lesson notebook

Build `16-more-strategies/lesson.ipynb` via `build_ch16_notebook.py`. Cells import the four helper modules; each family section follows the same 6-cell template per spec §2/§3/§4.

Cell list (long — this is a large chapter):

- `title` (markdown) — title + spec link + 4-sentence overview (3 families + cross-family question).
- `s1-head` + `s1-load` — load QQQ, recap Ch7 four-family map, state Ch16 question, five-step pipeline checklist.
- **§2 Momentum** (6 cells):
  - `s2-1-lag-sweep` (code: lag-k autocorr table + plot) + `s2-1-interp` (markdown).
  - `s2-2-backtest` (code: event-driven backtest at working (N, K)).
  - `s2-3-cost-sweep` (code: k_σ sweep with pre/post-cost Sharpe; plot).
  - `s2-4-execution` (code: passive entry sim + toxicity table) + `s2-4-interp` (markdown: "momentum takes").
  - `s2-5-regime` (code: Sharpe stratified by Ch15 §5.1 / §5.2 / §5.3 indicators).
  - `s2-6-verdict` (markdown table + 1-paragraph verdict).
- **§3 Breakout** (6 cells, same template):
  - `s3-1-or-stats` (code: OR-width distribution; sessions with break).
  - `s3-2-backtest` (code: confirmation + anticipation backtests).
  - `s3-3-2d-sweep` (code: OR-percentile × eps Sharpe surface).
  - `s3-4-execution` (code: toxicity decomposition on anticipation variant).
  - `s3-5-regime` (code: Sharpe stratified by Ch15 indicators).
  - `s3-6-verdict` (markdown table + verdict).
- **§4 Event-driven** (5 cells — compressed per spec §4):
  - `s4-1-windows` (code: pre/release/post window log-returns table).
  - `s4-2-backtest` (code: both H1 + H2 trade ledgers, Bootstrap CI).
  - `s4-3-cost` (code: post-cost numbers; CI annotations).
  - `s4-4-honesty` (markdown: sample-size disclaimer; forward to Exercise 3).
  - `s4-5-verdict` (markdown table + verdict).
- **§5 Cross-family** (3 cells):
  - `s5-1-deflation-table` (markdown table assembling §2.6, §3.6, §4.5 numbers).
  - `s5-2-regime-fingerprint` (code: family × regime Sharpe heatmap).
  - `s5-3-pick-candidate` (markdown: verdict — match one of three pre-stated outcomes).
- `s6-head` (markdown) — So what + Key Terms + Up next.
- `exercises` (markdown) — 4 prompts.
- `ex1-solution` + `ex4-solution` (code + markdown) — worked solutions for Exercises 1 and 4 (per spec; 2 and 3 stay as prompts).

- [ ] **Step 2.1: Write `build_ch16_notebook.py`** that assembles all the cells above. Each code cell pastes a verbatim slice of the pre-flight script. Add `# ...` comments on non-obvious lines (the per-session OR-width groupby, the toxicity formula, the bootstrap loop) per `feedback_comment_nonobvious_code`.

- [ ] **Step 2.2:** Run `python build_ch16_notebook.py && jupyter nbconvert --execute --inplace 16-more-strategies/lesson.ipynb`. Confirm zero errors and that every printed number matches `/tmp/ch16_findings.md` exactly.

- [ ] **Step 2.3: Page-count check.** Open the executed notebook; count rendered cells. Target ≤ 60 cells total. If over, apply spec §"scope hedges" cuts in this order:
  - Compress §2.5 / §3.6 regime conditioning into §5.2 only.
  - Drop §3 breakout-anticipation variant; keep only confirmation; mention anticipation in §6 So-What.
  - Demote §4 event-driven to "single backtest cell + Exercise 3 carries the rest."

- [ ] **Step 2.4: Checkpoint.**

---

## Task 3: README

Build `16-more-strategies/README.md` — the chapter's narrative anchor. This is the longest README in the curriculum (spec §"~25 pages").

Required content per section:

- **§1 Setup.** Recap Ch7's four families. State the chapter's question. Five-step pipeline checklist. Honest framing: most families expected to fail; verdict matters less than the pipeline's fairness.
- **§2 Momentum.** Each sub-section §2.1–§2.6 gets a paragraph; the cost-aware sweep gets a where-clause table for k_σ, σ̂_t, N, K. Push-interpretation paragraph per family verdict per `feedback_push_interpretations_past_description`.
- **§3 Breakout.** Same six-sub-section structure. Define "opening range," "false break," "stop-limit" inline per `feedback_define_every_term`. The 2D Sharpe surface and toxicity table both get standalone paragraphs.
- **§4 Event-driven.** Sample-size honesty up front and at end. CI on point estimate dominates the section's verdict; the framework lives, the conclusion defers to Exercise 3.
- **§5 Cross-family.** Deflation table; regime-fingerprint heatmap interpretation; §5.3 candidate-pick verdict (matching one of three pre-stated outcomes — choose the one whose data we actually see).
- **§6 So what + Key Terms + Up next.** Three decision rules. Forward pointer to Ch17-18 (futures mechanics + going live).

**Key Terms (target 10):** momentum, opening range, breakout confirmation, breakout anticipation, false break, event-driven strategy, pre-release drift, post-release continuation, regime fingerprint, family-dependent execution.

**Cross-chapter linking:**
- Ch7 §3-5 family definitions → instantiated in §2/§3/§4.
- Ch7 §6 lag-120 hint → empirically pursued in §2.1.
- Ch7 §7 regime-change driver → re-paid in §5.2.
- Ch9-13 pipeline → reused as the fairness instrument.
- Ch12 §promise (each family clears cost bar; most fail) → paid in §2.3, §3.4, §4.3, §5.1.
- Ch13 §promise (family-dependent execution) → paid in §2.4, §3.5, §4.4.
- Ch14 §promise (Kelly on a real candidate) → paid in §5.3.
- Ch15 §promise (regime indicators as conditioning) → paid in §2.5, §3.6, §5.2.

**Exercise prompts** (matching notebook 1:1):

1. **SPY transfer of the best-surviving family.** Re-run §2 / §3 / §4 (whichever survived) on SPY. Document the Sharpe gap and discuss why.
2. **ORB sensitivity to opening-range length.** Run §3 at OR-window ∈ {15, 30, 60} minutes. Apply Bonferroni across the 3 variants × 3 ε values = 9 candidate parameter combinations. Discuss the Ch10 §4 snooping inflation.
3. **Event-driven extended to CPI and NFP.** Re-run §4 across all three event types (FOMC + CPI + NFP). Does ~24 events instead of ~8 narrow the bootstrap CI enough for a verdict?
4. **Regime-gated combination.** Use Ch15 regime indicators to switch between MR (Ch11) and the best §2/§3/§4 family. Does the gated combination Sharpe beat either alone, *after costs*? Apply Ch10-style multiple-comparison discount on the gate-selection itself (the gate is a parameter chosen ex post).

Worked solutions for 1 and 4 in the notebook only (Ex4 is meaty — essentially a mini Ch11 walk-forward on the gate parameter); 2 and 3 stay as prompts.

- [ ] **Step 3.1:** Draft README section-by-section. Where the notebook prints a table, embed the rendered table (post-execution) in the README.
- [ ] **Step 3.2:** Verify all four exercise prompts byte-identical to notebook.
- [ ] **Step 3.3:** Run the README through the "no external knowledge leaps" check per `feedback_no_external_knowledge_leaps`: every reference to FOMC, CPI, NFP, BLS, "false break," "stop-limit," "anticipation vs confirmation," "regime fingerprint" gets an inline gloss the first time it appears.
- [ ] **Step 3.4: Checkpoint.**

---

## Task 4: Merged notebook

Build `16-more-strategies/lesson_merged.ipynb` interleaving README prose + lesson code cells per the Ch12-15 pattern.

Given the chapter's size, the merged notebook will be the longest in the curriculum. The interleave order is README-section → corresponding notebook code cells → README §X.Y prose → §X.Y code cells, drilling down per family. Worked solutions for Ex1 and Ex4 follow the exercise prompts.

- [ ] **Step 4.1:** Write `build_ch16_merged.py` importing the cell library used by the lesson builder. Re-use cell IDs.
- [ ] **Step 4.2:** Run + execute via `jupyter nbconvert --execute --inplace`. Confirm zero errors. Total execution wall-clock should be < 90s; if longer, investigate.
- [ ] **Step 4.3:** Verify exercise prompts byte-identical across README / lesson / merged.
- [ ] **Step 4.4: Checkpoint.**

---

## Task 5: Glue updates + commit

- [ ] **Step 5.1: `glossary.md`** — add the 10 Key Terms.

- [ ] **Step 5.2: Root `README.md`** — add Ch16 row. Note that Ch16 closes Part 8; Part 9 (Ch17-18, futures + going live) is next.

- [ ] **Step 5.3: Update `MEMORY.md` / `project_curriculum_roadmap.md`** Ch16 entry:
  - Spec + plan paths.
  - Three-flavor framing (momentum / breakout / event-driven).
  - Covered with empirical headlines per family (lag-k sweep result; ORB-confirm vs anticipate Sharpes; toxicity bp; FOMC 8-trade CI width).
  - Cross-family deflation table values.
  - §5.3 verdict — which of three pre-stated outcomes the data produced + the chosen Ch17-18 candidate (or "no clear candidate, paper-trading the discipline").
  - Mid-execution course corrections from Step 1.8 watchlist.
  - Promises honored (Ch7 four-family map + §6 lag-120 + §7 regime decay; Ch12 cost bar; Ch13 family-dependent execution; Ch14 candidate hunt; Ch15 regime conditioning).
  - Promises to honor in Ch17-18 (NQ mechanics on chosen candidate; live regime monitoring).

- [ ] **Step 5.4: Commit.** Stage only Ch16 paths per `feedback_isolate_in_progress_chapters`:

```bash
git add 16-more-strategies/ \
        docs/superpowers/specs/2026-05-13-ch16-more-strategies-design.md \
        docs/superpowers/plans/2026-05-13-ch16-more-strategies.md \
        glossary.md README.md
git diff --cached --stat   # verify no sibling-chapter files staged
git commit -m "$(cat <<'EOF'
Add Chapter 16 — More strategies (momentum, breakout, event-driven)

Runs the three non-MR strategy families through the same Ch9-13 pipeline
that deflated MR. Cross-family deflation table; Ch15 regime indicators as
conditioning variables; family-dependent execution per Ch13. Pre-states all
three §5.3 verdict outcomes; selects the candidate (or honest no-candidate)
for Ch17-18 paper-trading.
EOF
)"
```

- [ ] **Step 5.5:** `git status` clean. Update `MEMORY.md` Ch16 entry to ✅ DONE. Update curriculum roadmap "Part 8" section to note Part 8 is complete; "Part 9 — Futures and going live" is next.

---

## Self-review checklist

- [ ] Spec coverage: §1 → s1; §2 → s2-1..s2-6 (Momentum 6 sub-cells); §3 → s3-1..s3-6 (Breakout); §4 → s4-1..s4-5 (Event-driven); §5 → s5-1..s5-3 (cross-family); §6 → s6 + glossary. Every spec sub-section traces to a notebook cell and a README section.
- [ ] Placeholder scan: search for "TBD", "TODO", "see above", "fill in" — fix any.
- [ ] Symbol consistency across families: `N`, `K`, `k_σ`, `σ̂_t`, OR_low, OR_high, ε used identically in README math and module code. Family-specific symbols (`pre`, `release`, `post`, `H1`, `H2`) defined per family before use.
- [ ] Helper modules pass `test_helpers.py`.
- [ ] Four exercise prompts byte-identical across README / lesson / merged; worked solutions for Ex1 and Ex4 present in lesson + merged, absent from README.
- [ ] All formulas (momentum entry rule, OR break condition, toxicity, conditional Sharpe) have where-clauses.
- [ ] External-knowledge leaps caught: false break, stop-limit, anticipation vs confirmation, regime fingerprint, family-dependent execution, FOMC/CPI/NFP release mechanics.
- [ ] §5.3 verdict prose matches the actual data — not the spec's working hypothesis. If reality lands in a different one of the three pre-stated outcomes, use that narrative.
- [ ] Page count ≤ spec target ~25 pages; if over, apply scope hedges per Step 2.3.
- [ ] Memory roadmap entry includes the "which §5.3 outcome fired" note for future cross-chapter referencing.
