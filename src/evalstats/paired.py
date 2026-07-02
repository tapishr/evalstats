"""Paired comparison of two systems evaluated on the same task set.

When systems A and B run on the *same* tasks, the correct comparison is
paired: only the tasks where exactly one system succeeds (the discordant
pairs) carry information about the difference. Comparing the two marginal
scores as if they were independent samples throws away the pairing and can
be off by a large factor in either direction.
"""

from __future__ import annotations

import math
from collections.abc import Collection

from scipy.stats import binomtest, norm


def discordant_counts(
    resolved_a: Collection[str],
    resolved_b: Collection[str],
) -> tuple[int, int]:
    """Count discordant pairs between two systems' resolved-task sets.

    Args:
        resolved_a: task IDs solved by system A.
        resolved_b: task IDs solved by system B.

    Returns:
        (b, c) where b = tasks only A solved, c = tasks only B solved.
    """
    set_a, set_b = set(resolved_a), set(resolved_b)
    return len(set_a - set_b), len(set_b - set_a)


def mcnemar_pvalue(b: int, c: int) -> float:
    """Exact McNemar test on discordant counts.

    Tests H0: the two systems have equal success rates, using the exact
    binomial distribution of the discordant pairs (b successes-only-A out
    of b + c discordant, p = 0.5 under H0). Two-sided.

    Returns 1.0 when there are no discordant pairs (the data carry no
    information about a difference).
    """
    if b < 0 or c < 0:
        raise ValueError("counts must be non-negative")
    m = b + c
    if m == 0:
        return 1.0
    return binomtest(b, m, 0.5, alternative="two-sided").pvalue


def paired_diff_ci(
    b: int,
    c: int,
    n: int,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Difference in success rates with a paired (matched) CI.

    Args:
        b: tasks only system A solved.
        c: tasks only system B solved.
        n: total tasks both systems attempted.
        alpha: 1 - confidence level.

    Returns:
        (diff, lower, upper) where diff = (b - c) / n is A's advantage.

    Notes:
        Wald-type interval on the paired difference with standard error
        sqrt(b + c - (b - c)^2 / n) / n. Adequate for the discordant counts
        typical of agent benchmarks (tens of discordant pairs); at very
        small counts prefer reporting the exact McNemar p-value alongside.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if b + c > n:
        raise ValueError("b + c cannot exceed n")

    diff = (b - c) / n
    z = norm.ppf(1 - alpha / 2)
    se = math.sqrt(max(0.0, (b + c) - (b - c) ** 2 / n)) / n
    return diff, diff - z * se, diff + z * se
