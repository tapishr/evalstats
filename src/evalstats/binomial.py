"""Confidence intervals for single success rates."""

from __future__ import annotations

import math

from scipy.stats import norm


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    The default choice for benchmark success rates: unlike the naive Wald
    interval it behaves sensibly at extreme rates (k near 0 or n) and small N.

    Args:
        k: number of successes (e.g. tasks resolved).
        n: number of trials (e.g. tasks attempted).
        alpha: 1 - confidence level. 0.05 gives a 95% interval.

    Returns:
        (lower, upper) bounds on the true success rate.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k must be in [0, n]")

    z = float(norm.ppf(1 - alpha / 2))
    p_hat = k / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2))
    # At the boundaries the Wilson bound is exactly 0 (k=0) / 1 (k=n);
    # pin them so float error can't leak a spurious epsilon.
    lo = 0.0 if k == 0 else max(0.0, center - half)
    hi = 1.0 if k == n else min(1.0, center + half)
    return lo, hi
