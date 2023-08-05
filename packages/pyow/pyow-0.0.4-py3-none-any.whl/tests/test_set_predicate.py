import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_set():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `set` but received type `str`'):
        pyow('foo', pyow.set)


def test_set_size():
    pyow(set([1, 2, 3]), pyow.set.size(3))
    with pytest.raises(ArgumentError, match='Expected set to have size `3`, got `2`'):
        pyow(set([1, 2]), pyow.set.size(3))


def test_set_max_size():
    pyow(set([1, 2]), pyow.set.max_size(3))
    with pytest.raises(ArgumentError, match='Expected set to have maximum size of `3`, got `4`'):
        pyow(set([1, 2, 3, 4]), pyow.set.max_size(3))


def test_set_has():
    pyow(set([1, 2]), pyow.set.has(set([1, ])))
    pyow(set(['a', 'b']), pyow.set.has(set(['a', ])))
    pyow(set([1, 'a', 3, 4]), pyow.set.has(set([1, 'a'])))
    with pytest.raises(ArgumentError, match=re.escape('Expected set to have items {5, 6, 7}')):
        pyow(set([2, 2, 3, 4]), pyow.set.has(set([5, 6, 7])))


def test_set_has_any():
    pyow(set([1, 2]), pyow.set.has_any(set([1, 3, 5])))
    pyow(set([1, ]), pyow.set.has_any(set([1, 3, 5])))
    pyow(set(['a', 'b', 'c', 'f']), pyow.set.has_any(set(['a', 'f'])))
    with pytest.raises(ArgumentError, match=re.escape('Expected set to have any items {5, 6, 7}')):
        pyow(set([2, 2, 3, 4]), pyow.set.has_any(set([5, 6, 7])))


def test_set_deep_equal():
    pyow(set((1, 2)), pyow.set.deep_equal(set((1, 2))))
    pyow(set(['foo', 1, (1, 2, )]), pyow.set.deep_equal(set(['foo', 1, (1, 2, )])))
    with pytest.raises(ArgumentError, match=re.escape("Expected set to deep equal `['foo', 1]`, got `{2, 'foo'}`")):
        pyow(set(['foo', 2]), pyow.set.deep_equal(['foo', 1]))


def test_set_of_type():
    pyow(set([1, 2, 3]), pyow.set.of_type(pyow.number))
    pyow(set(['1', '2', '3']), pyow.set.of_type(pyow.string))
    pyow(set([True, True, False]), pyow.set.of_type(pyow.boolean))
    with pytest.raises(ArgumentError, match='Expected argument to be of type `int` but received type `str`'):
        pyow(set(['1', '2', '3']), pyow.set.of_type(pyow.number))


def test_set_empty():
    pyow(set(), pyow.set.empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected set to be empty, got `{1, 2}`')):
        pyow(set((1,2)), pyow.set.empty)


def test_set_non_empty():
    pyow(set((1, 2)), pyow.set.non_empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected set not to be empty, got `set()`')):
        pyow(set(), pyow.set.non_empty)
