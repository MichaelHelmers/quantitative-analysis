"""Smoke tests for pipeline.py + family modules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
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
