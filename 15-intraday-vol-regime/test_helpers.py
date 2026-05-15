"""Smoke tests for garch.py + hmm.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
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
    fit = fit_garch11(r)
    assert abs(fit["alpha"] + fit["beta"] - (true_alpha + true_beta)) < 0.1, \
        f"persistence off: {fit['alpha']+fit['beta']:.3f}"


def test_hmm_separates_two_variance_regimes():
    rng = np.random.default_rng(1)
    n = 1000
    states = np.zeros(n, dtype=int); states[n//2:] = 1
    obs = rng.normal(0.0, np.where(states == 0, 0.005, 0.020))
    res = fit_hmm_2state(obs)
    assert res["sigma2"][1] > res["sigma2"][0] * 4, \
        f"states not separated: sigma2={res['sigma2']}"


if __name__ == "__main__":
    test_garch_recovers_known_parameters()
    test_hmm_separates_two_variance_regimes()
    print("OK")
