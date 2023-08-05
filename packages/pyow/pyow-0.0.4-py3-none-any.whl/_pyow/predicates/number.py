from math import isfinite
from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate


class NumberPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(int, context)

    def in_range(self, start: int, stop: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be in range `{start}..{stop}`',
            'validator': lambda value: start <= value <= stop
        })

    def greater_than(self, number: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be greater than `{number}`',
            'validator': lambda value: value > number
        })

    def greater_than_or_equal(self, number: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be greater than or equal to `{number}`',
            'validator': lambda value: value >= number
        })

    def less_than(self, number: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be less than `{number}`',
            'validator': lambda value: value < number
        })

    def less_than_or_equal(self, number: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be less than or equal to `{number}`',
            'validator': lambda value: value <= number
        })

    def equal(self, number: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to equal `{number}`',
            'validator': lambda value: value == number
        })

    @property
    def integer(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be an integer',
            'validator': lambda value: type(value) == int
        })

    @property
    def finite(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be finite`',
            'validator': lambda value: isfinite(value)
        })

    @property
    def infinite(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be infinite`',
            'validator': lambda value: not isfinite(value)
        })

    @property
    def positive(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be positive',
            'validator': lambda value: value > 0
        })

    @property
    def negative(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be negative',
            'validator': lambda value: value < 0
        })
