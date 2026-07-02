import pytest

from evalstats import mdd_paired, needed_pairs


def test_mdd_headline_number():
    # SWE-bench Verified scale: N=500, 20% discordance -> ~5.6 points.
    assert mdd_paired(500, 0.20) == pytest.approx(0.056, abs=0.001)


def test_mdd_shrinks_with_n():
    assert mdd_paired(2000, 0.20) < mdd_paired(500, 0.20)


def test_mdd_grows_with_discordance():
    assert mdd_paired(500, 0.30) > mdd_paired(500, 0.10)


def test_needed_pairs_inverts_mdd():
    d = 0.20
    n = 500
    delta = mdd_paired(n, d)
    assert needed_pairs(delta, d) == pytest.approx(n, rel=0.01)


def test_two_point_gap_needs_thousands_of_tasks():
    assert needed_pairs(0.02, 0.20) > 3500


def test_validation():
    with pytest.raises(ValueError):
        mdd_paired(0, 0.2)
    with pytest.raises(ValueError):
        mdd_paired(500, 0.0)
    with pytest.raises(ValueError):
        needed_pairs(0.0, 0.2)
