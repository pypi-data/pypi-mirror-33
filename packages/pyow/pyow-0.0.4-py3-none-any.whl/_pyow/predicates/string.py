import re
from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate
from pyow.utils import vali_date


class StringPredicate(BasePredicate):

    def __init__(self, context: Any=None):
        super().__init__(str, context)

    def min_length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected string to have a minimum length of `{length}`, got `{value}`',
            'validator': lambda value: len(value) >= length,
        })

    def max_length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected string to have a maximum length of `{length}`, got `{value}`',
            'validator': lambda value: len(value) <= length,
        })

    def length(self, length: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected string to have length `{length}`, got `{value}`',
            'validator': lambda value: len(value) == length
        })

    def matches(self, regexp: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to match ``, got `{value}`", # TODO: Fix regexp
            'validator': lambda value: bool(re.search(regexp, value)),
        })

    def starts_with(self, search_string: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to start with `{search_string}`, got `{value}`",
            'validator': lambda value: value.startswith(search_string)
        })

    def ends_with(self, search_string: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to end with `{search_string}`, got `{value}`",
            'validator': lambda value: value.endswith(search_string)
        })

    def includes(self, search_string: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to include `{search_string}`, got `{value}`",
            'validator': lambda value: search_string in value
        })

    def equals(self, expected: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to be equal to `{expected}`, got `{value}`",
            'validator': lambda value: value == expected,
        })

    @property
    def alphanumeric(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to be alphanumeric, got `{value}`",
            'validator': lambda value: value.isalpha(),
        })

    @property
    def numeric(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to be numeric, got `{value}`",
            'validator': lambda value: value.isdigit(),
        })

    @property
    def date(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected string to be a date, got `{value}`",
            'validator': lambda value: vali_date(value),
        })

    @property
    def empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected string to be empty, got `{value}`',
            'validator': lambda value: value == ''
        })

    @property
    def non_empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected string not to be empty`',
            'validator': lambda value: value != ''
        })
