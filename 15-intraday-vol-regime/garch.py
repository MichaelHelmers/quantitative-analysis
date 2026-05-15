"""Hand-rolled GARCH(1,1) MLE — pure scipy. No `arch` dependency
(broken under pandas 3.0 per retired Ch9 plan)."""
import numpy as np
from scipy.optimize import minimize


def garch11_neg_log_lik(params, r):
    """GARCH(1,1) negative log-likelihood under Normal innovations.

    sigma^2_t = omega + alpha * r^2_{t-1} + beta * sigma^2_{t-1}
    where:
      r_t      = log-return at session t (mean-centered).
      omega>0  = baseline variance.
      alpha>=0 = ARCH coefficient (innovation impact).
      beta>=0  = GARCH coefficient (variance persistence).
      alpha+beta<1 = stationarity constraint.
    """
    omega, alpha, beta = params
    if omega <= 0 or alpha < 0 or beta < 0 or (alpha + beta) >= 1:
        return 1e10
    n = len(r)
    sigma2 = np.empty(n)
    sigma2[0] = r.var(ddof=0)   # initialize at unconditional variance
    for t in range(1, n):
        sigma2[t] = omega + alpha * r[t-1]**2 + beta * sigma2[t-1]
    # Normal log-likelihood (drop constant): -0.5 * sum(log sigma^2_t + r^2_t / sigma^2_t)
    return 0.5 * np.sum(np.log(sigma2) + r**2 / sigma2)


def fit_garch11(r, n_starts=8, seed=15):
    """Fit GARCH(1,1) by MLE with multi-start + Nelder-Mead polish.

    Returns dict with keys:
      omega, alpha, beta, sigma2, log_lik, n_starts, pinned_at_init.
    pinned_at_init is True when every start converged within 1e-6 of x0
    (a non-identification signal — typically on small samples).
    """
    rng = np.random.default_rng(seed)
    r = np.asarray(r) - np.mean(r)
    var = r.var() if r.var() > 0 else 1e-8

    starts = [
        (0.02 * var, 0.10, 0.85),   # Standard RiskMetrics-like
        (0.10 * var, 0.05, 0.90),   # High-persistence
        (0.50 * var, 0.20, 0.70),   # Mid-persistence
        (0.05 * var, 0.30, 0.50),   # Reactive
        (0.20 * var, 0.15, 0.80),   # Mid
    ]
    # Add random starts inside the stationarity region until we have n_starts
    while len(starts) < n_starts:
        a = rng.uniform(0.01, 0.30)
        b = rng.uniform(0.50, 0.99 - a)
        w = rng.uniform(0.01, 0.50) * var
        starts.append((w, a, b))

    best = None
    pinned_count = 0
    for x0 in starts:
        # Stage 1: L-BFGS-B with bounds
        try:
            res1 = minimize(
                garch11_neg_log_lik, x0, args=(r,),
                method="L-BFGS-B",
                bounds=[(1e-12, None), (0.0, 0.99), (0.0, 0.99)],
            )
            x1 = res1.x
        except Exception:
            x1 = np.asarray(x0)
        # Stage 2: Nelder-Mead polish (no bounds, but the neg-log-lik returns 1e10
        # outside the feasible region so the simplex stays inside)
        try:
            res2 = minimize(
                garch11_neg_log_lik, x1, args=(r,),
                method="Nelder-Mead",
                options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 2000},
            )
            x_final = res2.x
            ll = -res2.fun
        except Exception:
            x_final = x1
            ll = -garch11_neg_log_lik(x1, r)
        if (np.abs(np.array(x_final) - np.array(x0)) < 1e-6).all():
            pinned_count += 1
        if best is None or ll > best["log_lik"]:
            best = {
                "omega": float(x_final[0]),
                "alpha": float(x_final[1]),
                "beta": float(x_final[2]),
                "log_lik": float(ll),
                "x0": tuple(x0),
            }

    omega, alpha, beta = best["omega"], best["alpha"], best["beta"]
    sigma2 = np.empty(len(r))
    sigma2[0] = r.var()
    for t in range(1, len(r)):
        sigma2[t] = omega + alpha * r[t-1]**2 + beta * sigma2[t-1]
    return {
        "omega": omega, "alpha": alpha, "beta": beta,
        "sigma2": sigma2, "log_lik": best["log_lik"],
        "n_starts": len(starts),
        "pinned_at_init": pinned_count == len(starts),
    }


def long_run_variance(omega, alpha, beta):
    """Unconditional variance omega / (1 - alpha - beta)."""
    return omega / (1.0 - alpha - beta)
