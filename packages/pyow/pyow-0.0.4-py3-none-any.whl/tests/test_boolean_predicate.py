import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_boolean():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `bool` but received type `str`'):
        pyow('foo', pyow.boolean)


def test_true():
    pyow(True, pyow.boolean.true)
    with pytest.raises(ArgumentError, match='Expected `False` to be True'):
        pyow(False, pyow.boolean.true)


def test_false():
    pyow(False, pyow.boolean.false)
    with pytest.raises(ArgumentError, match='Expected `True` to be False'):
        pyow(True, pyow.boolean.false)
