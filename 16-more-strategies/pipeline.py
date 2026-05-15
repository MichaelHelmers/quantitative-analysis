"""Shared pipeline for Ch16 strategy families.

Reuses the Ch9 single-position event-driven loop with strategy-specific
signal and exit hooks. Cost stack is Ch12's (Roll's spread + IBKR commission +
square-root impact). Toxicity diagnostic is Ch13's (drift_uncond - drift_filled).
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
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

    signal_fn(day_df, i, state) -> (signal, K_max) or None
        Called once per bar (i) on the session's bar DataFrame.
        signal in {-1, 0, +1}, K_max is the max-hold in bars.
        state is a chapter-specific dict (e.g., {"opening_range": (lo, hi)}).
    state_init(day_df) -> dict
        Called once at session start to compute strategy-specific state.
    """
    name: str
    signal_fn: Callable
    state_init: Callable = field(default=lambda day: {})


def event_driven_backtest(rth: pd.DataFrame, strategy: Strategy) -> pd.DataFrame:
    """Single-position event-driven loop. Inherits Ch9 sec.2 conventions:
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
            if in_pos != 0 and K_remaining is not None and i - entry_i >= K_remaining:
                exit_i = min(i, len(day) - 1)
                exit_px = day.loc[exit_i, "open"] if exit_i < len(day) else day.loc[exit_i, "close"]
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
ROLL_HALF_SPREAD_BP = 0.72
COMMISSION_BP_PER_LEG = 0.07
IMPACT_ETA = 0.10
DAILY_SIGMA = 0.0102
ADV_USD = 15e9


def round_trip_cost_bp(q_usd: float = 30_000) -> float:
    """Round-trip cost in bp for a market-order strategy at notional q."""
    spread = 2 * ROLL_HALF_SPREAD_BP
    commission = 2 * COMMISSION_BP_PER_LEG
    impact_one_leg = IMPACT_ETA * DAILY_SIGMA * np.sqrt(q_usd / ADV_USD) * 1e4
    return spread + commission + 2 * impact_one_leg


def annualize_sharpe(pnl: pd.Series, n_sessions: int) -> float:
    if len(pnl) < 2 or pnl.std() == 0:
        return float("nan")
    tpy = len(pnl) / max(n_sessions, 1) * 252
    return (pnl.mean() / pnl.std()) * np.sqrt(tpy)


def toxicity_bp(filled_pnl: pd.Series, unconditional_pnl: pd.Series) -> float:
    return (unconditional_pnl.mean() - filled_pnl.mean()) * 1e4
