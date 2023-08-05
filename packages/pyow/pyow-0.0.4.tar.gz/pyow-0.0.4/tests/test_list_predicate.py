import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_list():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `list` but received type `str`'):
        pyow('foo', pyow.list)


def test_list_length():
    pyow([1, 2, 3], pyow.list.length(3))
    with pytest.raises(ArgumentError, match='Expected list to have length `3`, got `2`'):
        pyow([1, 2], pyow.list.length(3))


def test_list_min_length():
    pyow([1, 2, 3], pyow.list.min_length(3))
    with pytest.raises(ArgumentError, match='Expected list to have minimum length of `3`, got `2`'):
        pyow([1, 2], pyow.list.min_length(3))


def test_list_max_length():
    pyow([1, 2], pyow.list.max_length(3))
    with pytest.raises(ArgumentError, match='Expected list to have maximum length of `3`, got `4`'):
        pyow([1, 2, 3, 4], pyow.list.max_length(3))


def test_list_starts_with():
    pyow([1, 2], pyow.list.starts_with(1))
    pyow(['a', 'b'], pyow.list.starts_with('a'))
    pyow([[1,'a'], [3,4]], pyow.list.starts_with([1, 'a']))
    with pytest.raises(ArgumentError, match='Expected array to start with `1`, got `2`'):
        pyow([2, 2, 3, 4], pyow.list.starts_with(1))


def test_list_ends_with():
    pyow([1, 2], pyow.list.ends_with(2))
    pyow(['a', 'b'], pyow.list.ends_with('b'))
    pyow([[1,'a'], [3, 4]], pyow.list.ends_with([3, 4]))
    with pytest.raises(ArgumentError, match='Expected array to end with `2`, got `1`'):
        pyow([1, 3, 4, 5 , 1], pyow.list.ends_with(2))


def test_list_includes():
    pyow([1, 2, 3], pyow.list.includes(1, 2))
    with pytest.raises(ArgumentError, match=re.escape('Expected list to include all elements of `(4, 5)`, got `[1, 2, 3]`')):
        pyow([1, 2, 3], pyow.list.includes(4, 5))


def test_list_includes_any():
    pyow([1, 2, 3], pyow.list.includes_any(2, 5))
    with pytest.raises(ArgumentError, match=re.escape('Expected list to include any element of `(4, 5)`, got `[1, 2, 3]`')):
        pyow([1, 2, 3], pyow.list.includes_any(4, 5))


def test_list_empty():
    pyow([], pyow.list.empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected list to be empty, got `[1, 2, 3]`')):
        pyow([1, 2, 3], pyow.list.empty)


def test_list_non_empty():
    pyow([1, 2, 3], pyow.list.non_empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected list not to be empty, got `[]`')):
        pyow([], pyow.list.non_empty)


def test_list_deep_equal():
    pyow(['foo', ], pyow.list.deep_equal(['foo', ]))
    pyow(['foo', {'id': 1}], pyow.list.deep_equal(['foo', {'id': 1}]))
    with pytest.raises(ArgumentError, match=re.escape("Expected list to deep equal `['foo', {'id': 2}]`, got `['foo', {'id': 1}]`")):
        pyow(['foo', {'id': 1}], pyow.list.deep_equal(['foo', {'id': 2}]))


def test_list_of_type():
    pyow(['foo', 'bar'], pyow.list.of_type(pyow.string))
    pyow(['foo', 'bar'], pyow.list.of_type(pyow.string.min_length(3)))
    with pytest.raises(ArgumentError, match='Expected string to have a minimum length of `3`, got `b`'):
        pyow(['foo', 'b'], pyow.list.of_type(pyow.string.min_length(3)))
