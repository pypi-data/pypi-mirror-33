from typing import Callable, Any

from pyow.exceptions import ArgumentError
from pyow.operators.nix import nix
from pyow.types import Predicate


def validate_type(pred_type):
    if pred_type in (int, float):
        return lambda value: isinstance(value, (int, float))
    if pred_type == Exception:
        return lambda value: isinstance(value, Exception)

    return lambda value: type(value) is pred_type


class BasePredicate(object):
    def __init__(self, pred_type: Any, context: Any=None):
        self.context = context or {
            'validators': [],
        }

        self.add_validator({
            'message': lambda value, result=None: f'Expected argument to be of type `{pred_type.__name__}` but received type `{type(value).__name__}`',
            'validator': validate_type(pred_type)
        })

    @property
    def nix(self) -> Predicate:
        return nix(self)

    @property
    def isnot(self) -> Predicate:
        return nix(self)

    def add_validator(self, validator: object) -> Predicate:
        self.context['validators'].append(validator)
        return self

    def test(self, value: Any, pyow: Callable):
        for obj in self.context['validators']:
            result = obj['validator'](value)
            if type(result) != bool or not result:
                raise ArgumentError(obj['message'](value, result), pyow)

    def is_(self, fn: Callable):
        return self.add_validator({
            'message': lambda value, result=None: result or f'Expected `{value}` to pass custom validation function',
            'validator': lambda value: fn(value)
        })
