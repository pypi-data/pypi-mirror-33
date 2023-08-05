from typing import Any, Tuple

from pyow.exceptions import ArgumentError
from pyow.predicates.base_predicate import BasePredicate
from pyow.pyow_dupe import pyow_dupe
from pyow.types import Predicate
from pyow.utils import deep_eq, of_type


class ListPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(list, context)

    def length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to have length `{length}`, got `{len(value)}`',
            'validator': lambda value: len(value) == length
        })

    def min_length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to have minimum length of `{length}`, got `{len(value)}`',
            'validator': lambda value: len(value) >= length
        })

    def max_length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to have maximum length of `{length}`, got `{len(value)}`',
            'validator': lambda value: len(value) <= length
        })

    def starts_with(self, search_element: Any) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected array to start with `{search_element}`, got `{value[0]}`',
            'validator': lambda value: value[0] == search_element
        })

    def ends_with(self, search_element: Any) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected array to end with `{search_element}`, got `{value[-1]}`',
            'validator': lambda value: value[-1] == search_element
        })

    def includes(self, *args: Tuple[Any]) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to include all elements of ``, got ``', # TODO: Fix list string
            'validator': lambda value: all(elem in value for elem in args)

        })

    def includes_any(self, *args: Tuple[Any]) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to include any element of ``, got ``',  # TODO: Fix list string
            'validator': lambda value: any(elem in value for elem in args)
        })

    def deep_equal(self, list_for_comparison: Any) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to deep equal ``, got ``',  # TODO: Fix list string
            'validator': lambda value: deep_eq(value, list_for_comparison)
        })

    def of_type(self, predicate: Predicate) -> Predicate:
        errors = []

        return self.add_validator({
            'message': lambda value, result=None: ''.join(errors),
            'validator': lambda value: of_type(value, predicate, errors)
        })

    @property
    def empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list to be empty, got ``',  # TODO: Fix list string
            'validator': lambda value: not bool(value),
        })

    @property
    def non_empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected list not to be empty, got ``',  # TODO: Fix list string
            'validator': lambda value: bool(value),
        })


