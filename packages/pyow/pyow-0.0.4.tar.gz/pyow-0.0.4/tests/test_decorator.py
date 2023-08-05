import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError, ArgumentMismatchError
from pyow.decorators import validate


def test_decorator_not_raises():
    @validate(
        pyow.string.max_length(3),
    )
    def mock_fn(first_arg):
        return first_arg

    mock_fn('mon')


def test_decorator_raises():
    @validate(
        pyow.string.max_length(3),
        pyow.string.min_length(2),
    )
    def mock_fn(first_arg, second_arg):
        return first_arg, second_arg

    with pytest.raises(ArgumentError, match='Expected string to have a maximum length of `3`, got `monkey`'):
        mock_fn('monkey', 'a12')


def test_decorator_argument_mismatch():
    @validate(
        pyow.string.max_length(3),
        pyow.string.min_length(2),
    )
    def mock_fn(*args, **kwargs):
        return 1

    with pytest.raises(ArgumentMismatchError, match='Function got `3` arguments, expected `2`'):
        mock_fn('monkey', 'a12', {'key': 'word', })


def test_decorator_kwargs():
    @validate(
        pyow.string.min_length(2),
        pyow.dict.size(2)
    )
    def mock_fn(*args, **kwargs):
        return 1

    mock_fn('apa', a=1, b=2)
