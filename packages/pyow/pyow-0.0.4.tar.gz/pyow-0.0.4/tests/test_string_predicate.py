import re
import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_string():
    with pytest.raises(ArgumentError, match='Expected argument to be of type `str` but received type `int`'):
        pyow(1, pyow.string)


def test_non_empty_string():
    pyow('foo', pyow.string.non_empty)
    with pytest.raises(ArgumentError, match='Expected string not to be empty'):
        pyow('', pyow.string.non_empty)


def test_empty_string():
    pyow('', pyow.string.empty)
    with pytest.raises(ArgumentError, match='Expected string to be empty, got `string`'):
        pyow('string', pyow.string.empty)


def test_min_length():
    pyow('strin', pyow.string.min_length(5))
    with pytest.raises(ArgumentError, match='Expected string to have a minimum length of `5`, got `stri`'):
        pyow('stri', pyow.string.min_length(5))


def test_max_length():
    pyow('strig', pyow.string.max_length(5))
    with pytest.raises(ArgumentError, match='Expected string to have a maximum length of `5`, got `string`'):
        pyow('string', pyow.string.max_length(5))


def test_length():
    pyow('string', pyow.string.length(6))
    with pytest.raises(ArgumentError, match='Expected string to have length `6`, got `strig`'):
        pyow('strig', pyow.string.length(6))


def test_matches():
    pyow('foo', pyow.string.matches('^f.o$'))
    with pytest.raises(ArgumentError, match=re.escape('Expected string to match `^f.o$`, got `Foo`')):
        pyow('Foo', pyow.string.matches('^f.o$'))


def test_starts_with():
    pyow('foobar', pyow.string.starts_with('foo'))
    with pytest.raises(ArgumentError, match='Expected string to start with `foo`, got `fuubar'):
        pyow('fuubar', pyow.string.starts_with('foo'))


def test_ends_with():
    pyow('foobar', pyow.string.ends_with('bar'))
    with pytest.raises(ArgumentError, match='Expected string to end with `bar`, got `foobaz`'):
        pyow('foobaz', pyow.string.ends_with('bar'))


def test_includes():
    pyow('foobar', pyow.string.includes('oba'))
    with pytest.raises(ArgumentError, match='Expected string to include `oba`, got `foofoo`'):
        pyow('foofoo', pyow.string.includes('oba'))


def test_equals():
    pyow('foobar', pyow.string.equals('foobar'))
    with pytest.raises(ArgumentError, match='Expected string to include `oba`, got `foofoo`'):
        pyow('foofoo', pyow.string.includes('oba'))


def test_alphanumeric():
    pyow('foobar', pyow.string.alphanumeric)
    with pytest.raises(ArgumentError, match='Expected string to be alphanumeric, got `foofoo 1`'):
        pyow('foofoo 1', pyow.string.alphanumeric)


def test_numeric():
    pyow('123', pyow.string.numeric)
    with pytest.raises(ArgumentError, match='Expected string to be numeric, got `foo`'):
        pyow('foo', pyow.string.numeric)


def test_date():
    pyow('2015-12-15T12:00:00Z', pyow.string.date)
    pyow('2015-12-15T12:00:00+01:00', pyow.string.date)
    with pytest.raises(ArgumentError, match='Expected string to be a date, got `foo`'):
        pyow('foo', pyow.string.date)
