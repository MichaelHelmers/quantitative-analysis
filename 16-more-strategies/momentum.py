"""Trailing N-min momentum on QQQ. Mirror of Ch8's MR with sign flipped.
Empirical hook: Ch7 sec.6 lag-120 rho = +0.004."""
import numpy as np
import pandas as pd
from pipeline import Strategy


def momentum_lag_sweep(rth: pd.DataFrame, lags=(1, 5, 30, 60, 120, 240, 390)):
    """Lag-k autocorrelation of 1-min log returns within sessions only."""
    out = {}
    for k in lags:
        rhos = []
        for _, day in rth.groupby("session_date"):
            r = day["log_ret"].dropna().values
            if len(r) > k + 1:
                rhos.append(np.corrcoef(r[k:], r[:-k])[0, 1])
        out[k] = float(np.nanmean(rhos))
    return out


def make_momentum_strategy(N: int, K: int, k_sigma: float, sigma_t_lookup) -> Strategy:
    """N-min trailing momentum; entry when |r_{t,t-N}| > k_sigma * sigma_t * sqrt(N/60); hold K."""
    def state_init(day):
        return {"N": N, "K": K, "k_sigma": k_sigma}

    def signal_fn(day, i, state):
        N_, K_, ks = state["N"], state["K"], state["k_sigma"]
        if i < N_:
            return None
        mos = int(day.loc[i, "minute_of_session"])
        if mos + K_ >= 390:
            return None
        prior = np.log(day.loc[i, "close"] / day.loc[i-N_, "close"])
        s = sigma_t_lookup(day.loc[i, "session_date"], mos)
        if np.isnan(s) or s <= 0:
            return None
        threshold = ks * s * np.sqrt(N_ / 60.0)
        if prior > threshold:
            return (+1, K_)
        elif prior < -threshold:
            return (-1, K_)
        return None

    return Strategy(name=f"Momentum N={N} K={K} k={k_sigma}",
                    signal_fn=signal_fn, state_init=state_init)
