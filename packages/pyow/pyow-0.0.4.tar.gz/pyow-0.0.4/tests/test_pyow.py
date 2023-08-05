import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_pyow_is_valid():
    assert pyow.is_valid(1, pyow.number)
    assert pyow.is_valid('str', pyow.string)
    assert pyow.is_valid('str', pyow.string.length(3))
    assert not pyow.is_valid('str', pyow.string.min_length(5))


def test_create_reusable_validator():
    string_check = pyow.create(pyow.string.min_length(6))

    string_check('foobar')
    string_check('foobars')
    string_check('foobarsy')
    with pytest.raises(ArgumentError):
        string_check('foo')


def test_nix_operator():
    pyow(1, pyow.number.nix.infinite)
    pyow(1, pyow.number.nix.infinite.greater_than(5))
    pyow('monkey!', pyow.string.nix.alphanumeric)

    with pytest.raises(ArgumentError, match=re.escape('[NOT] Expected string to be empty, got ``')):
        pyow('', pyow.string.nix.empty)


def test_isnot_operator():
    pyow(1, pyow.number.isnot.infinite)
    pyow(1, pyow.number.isnot.infinite.greater_than(5))
    pyow('monkey!', pyow.string.isnot.alphanumeric)

    with pytest.raises(ArgumentError, match=re.escape('[NOT] Expected string to be empty, got ``')):
        pyow('', pyow.string.isnot.empty)


def test_is_():
    pyow(1, pyow.number.is_(lambda x: x < 10))
    with pytest.raises(ArgumentError, match='Expected `1` to pass custom validation function'):
        pyow(1, pyow.number.is_(lambda x: x > 10))

    with pytest.raises(ArgumentError, match=re.escape('Expected `1` to be greater than `5`')):
        def greater_than(max_num: int, x: int):
            return x > max_num or f'Expected `{x}` to be greater than `{max_num}`'

        pyow(1, pyow.number.is_(lambda x: greater_than(5, x)))

        
def test_any():
    pyow('foo', pyow.any(pyow.string.max_length(4), pyow.number))
    with pytest.raises(ArgumentError, message='Any predicate failed with the following errors\n - Expected string to have a maximum length of `2`, got `foo`\n - Expected argument to be of type `int` but received type `str`'):
        pyow('foo', pyow.any(pyow.string.max_length(2), pyow.number))
