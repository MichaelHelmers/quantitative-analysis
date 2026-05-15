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
        # Note: transition matrix A held fixed during EM (simplified Baum-Welch).
        # Full xi-update would re-estimate A, but for this chapter's pedagogy
        # the fixed-A variant is enough — exercises can extend to full B-W.
    # Sort states by variance so state 1 is always high-vol
    if sigma2[0] > sigma2[1]:
        mu, sigma2 = mu[::-1], sigma2[::-1]
        gamma = gamma[:, ::-1]
        A = A[::-1, ::-1]
    return {"mu": mu, "sigma2": sigma2, "A": A, "gamma": gamma, "log_lik": log_lik}
