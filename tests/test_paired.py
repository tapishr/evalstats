import pytest

from evalstats import discordant_counts, mcnemar_pvalue, paired_diff_ci


def test_discordant_counts_basic():
    a = {"t1", "t2", "t3"}
    b = {"t2", "t3", "t4", "t5"}
    assert discordant_counts(a, b) == (1, 2)


def test_mcnemar_symmetric_is_one():
    assert mcnemar_pvalue(10, 10) == pytest.approx(1.0)


def test_mcnemar_no_discordance_is_one():
    assert mcnemar_pvalue(0, 0) == 1.0


def test_mcnemar_extreme_asymmetry():
    # 10 discordant pairs, all favoring A: p = 2 * 0.5^10
    assert mcnemar_pvalue(10, 0) == pytest.approx(2 * 0.5**10)


def test_mcnemar_leaderboard_scale_gap_not_significant():
    # A 10-task gap (2 points on N=500) with ~90 discordant pairs: noise.
    p = mcnemar_pvalue(50, 40)
    assert p > 0.3


def test_paired_diff_ci_zero_diff_symmetric():
    diff, lo, hi = paired_diff_ci(30, 30, 500)
    assert diff == 0.0
    assert lo == pytest.approx(-hi)


def test_paired_diff_ci_contains_point_estimate():
    diff, lo, hi = paired_diff_ci(55, 35, 500)
    assert lo < diff < hi
    assert diff == pytest.approx(20 / 500)


def test_paired_diff_ci_validates():
    with pytest.raises(ValueError):
        paired_diff_ci(300, 300, 500)
