import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_tuple():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `tuple` but received type `str`'):
        pyow('foo', pyow.tuple)


def test_tuple_length():
    pyow((1, 2, 3), pyow.tuple.length(3))
    with pytest.raises(ArgumentError, match='Expected tuple to have length `3`, got `2`'):
        pyow((1, 2), pyow.tuple.length(3))


def test_tuple_min_length():
    pyow((1, 2, 3), pyow.tuple.min_length(3))
    with pytest.raises(ArgumentError, match='Expected tuple to have minimum length of `3`, got `2`'):
        pyow((1, 2), pyow.tuple.min_length(3))


def test_tuple_max_length():
    pyow((1, 2), pyow.tuple.max_length(3))
    with pytest.raises(ArgumentError, match='Expected tuple to have maximum length of `3`, got `4`'):
        pyow((1, 2, 3, 4), pyow.tuple.max_length(3))


def test_tuple_starts_with():
    pyow((1, 2), pyow.tuple.starts_with(1))
    pyow(('a', 'b'), pyow.tuple.starts_with('a'))
    pyow(((1, 'a'), (3, 4)), pyow.tuple.starts_with((1, 'a')))
    with pytest.raises(ArgumentError, match='Expected tuple to start with `1`, got `2`'):
        pyow((2, 2, 3, 4), pyow.tuple.starts_with(1))


def test_tuple_ends_with():
    pyow((1, 2), pyow.tuple.ends_with(2))
    pyow(('a', 'b'), pyow.tuple.ends_with('b'))
    pyow(((1, 'a'), (3, 4)), pyow.tuple.ends_with((3, 4)))
    with pytest.raises(ArgumentError, match='Expected tuple to end with `2`, got `1`'):
        pyow((1, 3, 4, 5, 1), pyow.tuple.ends_with(2))


def test_tuple_includes():
    pyow((1, 2, 3), pyow.tuple.includes(1, 2))
    with pytest.raises(ArgumentError, match=re.escape('Expected tuple to include all elements of `(4, 5)`, got `(1, 2, 3)`')):
        pyow((1, 2, 3), pyow.tuple.includes(4, 5))


def test_tuple_includes_any():
    pyow((1, 2, 3), pyow.tuple.includes_any(2, 5))
    with pytest.raises(ArgumentError, match=re.escape('Expected tuple to include any element of `(4, 5)`, got `(1, 2, 3)`')):
        pyow((1, 2, 3), pyow.tuple.includes_any(4, 5))


def test_tuple_empty():
    pyow((), pyow.tuple.empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected tuple to be empty, got `(1, 2, 3)`')):
        pyow((1, 2, 3), pyow.tuple.empty)


def test_tuple_non_empty():
    pyow((1, 2, 3), pyow.tuple.non_empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected tuple not to be empty, got `()`')):
        pyow((), pyow.tuple.non_empty)


def test_tuple_deep_equal():
    pyow(('foo', ), pyow.tuple.deep_equal(('foo', )))
    pyow(('foo', {'id': 1}), pyow.tuple.deep_equal(('foo', {'id': 1})))
    with pytest.raises(ArgumentError, match=re.escape("Expected tuple to deep equal `('foo', {'id': 2})`, got `('foo', {'id': 1})`")):
        pyow(('foo', {'id': 1}), pyow.tuple.deep_equal(('foo', {'id': 2})))


def test_tuple_of_type():
    pyow(('foo', 'bar'), pyow.tuple.of_type(pyow.string))
    pyow(('foo', 'bar'), pyow.tuple.of_type(pyow.string.min_length(3)))
    with pytest.raises(ArgumentError, match='Expected string to have a minimum length of `3`, got `b`'):
        pyow(('foo', 'b'), pyow.tuple.of_type(pyow.string.min_length(3)))
