from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate
from pyow.utils import of_type, deep_eq


class DictPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(dict, context)

    def size(self, size: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict to have size `{size}`, got `{len(value)}`',
            'validator': lambda value: len(value) == size
        })

    def min_size(self, min_size: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict to have minimum size of `{min_size}`, got `{len(value)}`',
            'validator': lambda value: len(value) >= min_size
        })

    def max_size(self, max_size: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict to have maximum size of `{max_size}`, got `{len(value)}`',
            'validator': lambda value: len(value) <= max_size
        })

    def has_keys(self, keys: list) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected dict to have keys `{', '.join(keys)}`",
            'validator': lambda value: all(key in value.keys() for key in keys)
        })

    def has_any_keys(self, keys: list) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected dict to have any of the keys `{', '.join(keys)}`",
            'validator': lambda value: any(key in value.keys() for key in keys)
        })

    def has_values(self, values: list) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected dict to have values `{', '.join([str(x) for x in values])}`",
            'validator': lambda value: all(v in value.values() for v in values)
        })

    def has_any_values(self, values: list) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected dict to have any of the values `{', '.join([str(x) for x in values])}`",
            'validator': lambda value: any(v in value.values() for v in values)
        })

    def keys_of_type(self, predicate: Predicate) -> Predicate:
        errors = []

        return self.add_validator({
            'message': lambda value, result=None: ''.join(errors),
            'validator': lambda value: of_type(value.keys(), predicate, errors)
        })

    def values_of_type(self, predicate: Predicate) -> Predicate:
        errors = []

        return self.add_validator({
            'message': lambda value, result=None: ''.join(errors),
            'validator': lambda value: of_type(value.values(), predicate, errors)
        })

    @property
    def empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict to be empty, got ``',  # TODO: Fix dict string
            'validator': lambda value: not bool(value),
        })

    @property
    def non_empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict not to be empty, got ``',  # TODO: Fix dict string
            'validator': lambda value: bool(value),
        })

    def deep_equal(self, expected: dict) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected dict to deep equal ``, got ``',  # TODO: Fix dict string
            'validator': lambda value: deep_eq(value, expected)
        })
