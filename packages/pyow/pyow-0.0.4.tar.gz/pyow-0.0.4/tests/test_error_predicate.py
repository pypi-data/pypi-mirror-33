import pytest

from pyow import pyow
from pyow.exceptions import ArgumentError


def test_error():
    pyow(Exception('foo'), pyow.error)
    with pytest.raises(ArgumentError, match='Expected argument to be of type `Exception` but received type `str`'):
        pyow('foo', pyow.error)


def test_error_name():
    pyow(Exception('foo'), pyow.error.name('Exception'))
    with pytest.raises(ArgumentError, match='Expected error to have name `Exception`, got `ValueError`'):
        pyow(ValueError('foo'), pyow.error.name('Exception'))


def test_error_message():
    pyow(ValueError('foo'), pyow.error.message('foo'))
    with pytest.raises(ArgumentError, match='Expected error message to be `bar`, got `foo`'):
        pyow(ValueError('foo'), pyow.error.message('bar'))


def test_error_message_includes():
    pyow(SyntaxError('foo is not valid syntax'), pyow.error.message_includes('valid syntax'))
    pyow(SyntaxError('foo'), pyow.error.message_includes('o'))
    pyow(ValueError('value'), pyow.error.message_includes('val'))
    with pytest.raises(ArgumentError, match='Expected error message to include `unicorn`, got `foo bar`'):
        pyow(SyntaxError('foo bar'), pyow.error.message_includes('unicorn'))


def test_error_has_keys():
    error = ValueError('value')
    error.monkey = 1
    error.unicorn = 'fivel'

    pyow(error, pyow.error.has_keys(['monkey', 'unicorn']))
    with pytest.raises(ArgumentError, match='Expected error to have keys `unicorn`'):
        pyow(SyntaxError('foo bar'), pyow.error.has_keys(['unicorn']))


def test_error_instance_of():
    pyow(ValueError('e'), pyow.error.instance_of(ValueError))
    pyow(SyntaxError('e'), pyow.error.instance_of(Exception))
    pyow(TabError('e'), pyow.error.instance_of(SyntaxError))
    pyow(TabError('e'), pyow.error.instance_of(Exception))
    with pytest.raises(ArgumentError, match='Expected error `ValueError` to be instance of `SyntaxError`'):
        pyow(ValueError('foo bar'), pyow.error.instance_of(SyntaxError))
