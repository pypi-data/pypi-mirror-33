import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_dict():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `dict` but received type `str`'):
        pyow('foo', pyow.dict)


def test_dict_size():
    pyow({'a': 1}, pyow.dict.size(1))
    with pytest.raises(ArgumentError, match='Expected dict to have size `1`, got `2`'):
        pyow({'a': 1, 'b': 2}, pyow.dict.size(1))


def test_dict_min_size():
    pyow({'a': 1, 'b': 1, 'c': 1, 'd': 1}, pyow.dict.min_size(3))
    with pytest.raises(ArgumentError, match='Expected dict to have minimum size of `5`, got `4`'):
        pyow({'a': 1, 'b': 1, 'c': 1, 'd': 1}, pyow.dict.min_size(5))


def test_dict_max_size():
    pyow({'a': 1, 'b': 1, 'c': 1}, pyow.dict.max_size(3))
    with pytest.raises(ArgumentError, match='Expected dict to have maximum size of `3`, got `4`'):
        pyow({'a': 1, 'b': 1, 'c': 1, 'd': 1}, pyow.dict.max_size(3))


def test_dict_has_keys():
    pyow({'a': 1, 'b': 1, 'c': 1}, pyow.dict.has_keys(['a', 'b', 'c']))
    with pytest.raises(ArgumentError, match='Expected dict to have keys `a, b, c, d`'):
        pyow({'a': 1, 'b': 1, 'c': 1}, pyow.dict.has_keys(['a', 'b', 'c', 'd']))


def test_dict_has_any_keys():
    pyow({'a': 1, 'b': 1, 'c': 1}, pyow.dict.has_any_keys(['a', 'c', 'd']))
    with pytest.raises(ArgumentError, match='Expected dict to have any of the keys `a, c, f`'):
        pyow({'g': 1, 'h': 1, 'i': 1}, pyow.dict.has_any_keys(['a', 'c', 'f', ]))


def test_dict_has_values():
    pyow({'a': 1, 'b': 1, 'c': 1}, pyow.dict.has_values([1, 1, 1]))
    with pytest.raises(ArgumentError, match='Expected dict to have values `1, 2, 3`'):
        pyow({'g': 1, 'h': 1, 'i': 2}, pyow.dict.has_values([1, 2, 3]))


def test_dict_has_any_values():
    pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.has_any_values([1, 4, 5]))
    with pytest.raises(ArgumentError, match='Expected dict to have any of the values `1, 2, 3`'):
        pyow({'g': 4, 'h': 5, 'i': 62}, pyow.dict.has_any_values([1, 2, 3]))


def test_dict_has_keys_of_type():
    pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.keys_of_type(pyow.string))
    with pytest.raises(ArgumentError, match='Expected argument to be of type `str` but received type `int`'):
        pyow({1: 4, 2: 5, 3: 62}, pyow.dict.keys_of_type(pyow.string))


def test_dict_has_values_of_type():
    pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.values_of_type(pyow.number))
    with pytest.raises(ArgumentError, match='Expected argument to be of type `str` but received type `int`'):
        pyow({'g': 4, 'h': 5, 'i': 62}, pyow.dict.values_of_type(pyow.string))


def test_dict_empty():
    pyow({}, pyow.dict.empty)
    with pytest.raises(ArgumentError, match=re.escape("Expected dict to be empty, got `{'g': 4, 'h': 5, 'i': 62}`")):
        pyow({'g': 4, 'h': 5, 'i': 62}, pyow.dict.empty)


def test_dict_is_non_empty():
    pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.non_empty)
    with pytest.raises(ArgumentError, match=re.escape('Expected dict not to be empty, got `{}`')):
        pyow({}, pyow.dict.non_empty)


def test_dict_is_deep_equal():
    pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.deep_equal({'a': 1, 'b': 2, 'c': 4}))
    with pytest.raises(ArgumentError, match=re.escape("Expected dict to deep equal `{'d': 1, 'b': 2, 'c': 4}`, got `{'a': 1, 'b': 2, 'c': 4}`")):
        pyow({'a': 1, 'b': 2, 'c': 4}, pyow.dict.deep_equal({'d': 1, 'b': 2, 'c': 4}))
