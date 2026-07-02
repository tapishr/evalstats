"""Power analysis: what difference can a benchmark actually detect?

The quantity that matters when reading a leaderboard is not the reported
delta but the benchmark's *minimal detectable difference* (MDD): the gap
below which observed differences are more plausibly noise than signal.
"""

from __future__ import annotations

import math

from scipy.stats import norm


def mdd_paired(
    n: int,
    discordance: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> float:
    """Minimal detectable difference for a paired comparison.

    Args:
        n: number of tasks both systems attempt.
        discordance: expected fraction of tasks where exactly one system
            succeeds. On agent benchmarks between systems of similar
            strength this is typically 0.10-0.30.
        alpha: two-sided significance level.
        power: desired probability of detecting a true difference.

    Returns:
        The smallest true success-rate difference detectable with the
        requested power (in absolute proportion, e.g. 0.056 = 5.6 points).

    Notes:
        Uses the normal approximation Var(diff) ~= discordance / n, valid
        when the true difference is small relative to the discordance rate
        (the regime of leaderboard-adjacent systems).
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 < discordance <= 1:
        raise ValueError("discordance must be in (0, 1]")

    z_a = norm.ppf(1 - alpha / 2)
    z_b = norm.ppf(power)
    return (z_a + z_b) * math.sqrt(discordance / n)


def needed_pairs(
    delta: float,
    discordance: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    """Tasks required to detect a success-rate difference of `delta`.

    Inverse of :func:`mdd_paired`. E.g. to certify a 2-point improvement
    at 20% discordance you need ~3,900 tasks — nearly 8x SWE-bench
    Verified's 500.
    """
    if delta <= 0:
        raise ValueError("delta must be positive")
    if not 0 < discordance <= 1:
        raise ValueError("discordance must be in (0, 1]")

    z_a = norm.ppf(1 - alpha / 2)
    z_b = norm.ppf(power)
    return math.ceil(discordance * ((z_a + z_b) / delta) ** 2)
