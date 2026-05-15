"""Opening Range Breakout (ORB) on QQQ.

OR_t = [low, high] of the first 30 minutes (minutes 0-29 of session t).
Two execution variants:
  - confirmation: enter at close of breaking bar (takes).
  - anticipation: stop-limit at OR_high + eps bp (long) / OR_low - eps bp (short) (makes).
"""
import numpy as np
import pandas as pd
from pipeline import Strategy

OR_WINDOW = 30   # Exercise 2 sweeps over {15, 30, 60}


def opening_range(day, window=OR_WINDOW):
    head = day[day["minute_of_session"] < window]
    if len(head) == 0:
        return (np.nan, np.nan)
    return (head["low"].min(), head["high"].max())


def make_breakout_confirmation(eps_bp: float = 0.0) -> Strategy:
    """Confirmation: enter on close of breaking bar."""
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
            return (+1, 390 - mos - 1)
        elif c < lower:
            state["fired"] = True
            return (-1, 390 - mos - 1)
        return None

    return Strategy(name=f"Breakout-confirm eps={eps_bp}bp",
                    signal_fn=signal_fn, state_init=state_init)


def make_breakout_anticipation(eps_bp: float = 5.0) -> Strategy:
    """Anticipation: stop-limit at OR_high + eps / OR_low - eps.
    Approximates fills by checking whether any bar's H/L touches the trigger."""
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

    return Strategy(name=f"Breakout-anticipate eps={eps_bp}bp",
                    signal_fn=signal_fn, state_init=state_init)
