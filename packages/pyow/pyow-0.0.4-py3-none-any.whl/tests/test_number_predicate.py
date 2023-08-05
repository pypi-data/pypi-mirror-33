import math

import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_number():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `int` but received type `str`'):
        pyow('foo', pyow.number)


def test_in_range():
    pyow(10, pyow.number.in_range(0, 20))
    pyow(3, pyow.number.in_range(1, 5))
    with pytest.raises(ArgumentError, match='Expected `20` to be in range `0..10`'):
        pyow(20, pyow.number.in_range(0, 10))


def test_greater_than():
    pyow(10, pyow.number.greater_than(5))
    pyow(10, pyow.number.greater_than(5))
    with pytest.raises(ArgumentError, match='Expected `1` to be greater than `2`'):
        pyow(1, pyow.number.greater_than(2))


def test_greater_than_or_equal():
    pyow(10, pyow.number.greater_than_or_equal(8))
    pyow(10, pyow.number.greater_than_or_equal(3))
    with pytest.raises(ArgumentError, match='Expected `1` to be greater than or equal to `2`'):
        pyow(1, pyow.number.greater_than_or_equal(2))


def test_less_than():
    pyow(3, pyow.number.less_than(8))
    pyow(2, pyow.number.less_than(3))
    with pytest.raises(ArgumentError, match='Expected `3` to be less than `2`'):
        pyow(3, pyow.number.less_than(2))


def test_less_than_or_equal():
    pyow(3, pyow.number.less_than_or_equal(8))
    pyow(3, pyow.number.less_than_or_equal(3))
    with pytest.raises(ArgumentError, match='Expected `4` to be less than or equal to `2`'):
        pyow(4, pyow.number.less_than_or_equal(2))


def test_equal():
    pyow(3, pyow.number.equal(3))
    with pytest.raises(ArgumentError, match='Expected `4` to equal `2`'):
        pyow(4, pyow.number.equal(2))


def test_integer():
    pyow(3, pyow.number.integer)
    with pytest.raises(ArgumentError, match='Expected `4.1` to be an integer'):
        pyow(4.1, pyow.number.integer)


def test_finite():
    pyow(3, pyow.number.finite)
    with pytest.raises(ArgumentError, match='Expected `inf` to be finite'):
        pyow(math.inf, pyow.number.finite)


def test_infinite():
    pyow(math.inf, pyow.number.infinite)
    with pytest.raises(ArgumentError, match='Expected `4` to be infinite'):
        pyow(4, pyow.number.infinite)


def test_positive():
    pyow(3, pyow.number.positive)
    with pytest.raises(ArgumentError, match='Expected `-4` to be positive'):
        pyow(-4, pyow.number.positive)


def test_negative():
    pyow(-3, pyow.number.negative)
    with pytest.raises(ArgumentError, match='Expected `4` to be negative'):
        pyow(4, pyow.number.negative)


def test_nan():
    pyow(float('nan'), pyow.number.nan)
    with pytest.raises(ArgumentError, match='Expected `4` to be NaN'):
        pyow(4, pyow.number.nan)
