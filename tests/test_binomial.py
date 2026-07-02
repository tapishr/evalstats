import pytest

from evalstats import wilson_ci


def test_bounds_stay_in_unit_interval():
    lo, hi = wilson_ci(0, 100)
    assert lo == 0.0
    assert 0 < hi < 0.05

    lo, hi = wilson_ci(100, 100)
    assert 0.95 < lo < 1
    assert hi == 1.0


def test_half_rate_interval_is_centered():
    lo, hi = wilson_ci(50, 100)
    assert lo < 0.5 < hi
    assert abs((0.5 - lo) - (hi - 0.5)) < 1e-9


def test_interval_narrows_with_n():
    lo1, hi1 = wilson_ci(50, 100)
    lo2, hi2 = wilson_ci(500, 1000)
    assert (hi2 - lo2) < (hi1 - lo1)


def test_swebench_scale_width():
    # ~58% on 500 tasks: the CI alone spans ~±4.3 points.
    lo, hi = wilson_ci(292, 500)
    assert 0.54 < lo < 0.55
    assert 0.62 < hi < 0.63


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        wilson_ci(5, 0)
    with pytest.raises(ValueError):
        wilson_ci(-1, 10)
    with pytest.raises(ValueError):
        wilson_ci(11, 10)
