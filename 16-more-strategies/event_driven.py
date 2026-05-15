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
    tab = tab.copy()
    tab["h1_pnl_log"] = np.sign(tab["pre"]) * tab["release"]
    tab["h2_pnl_log"] = np.sign(tab["release"]) * tab["post"]
    return tab
