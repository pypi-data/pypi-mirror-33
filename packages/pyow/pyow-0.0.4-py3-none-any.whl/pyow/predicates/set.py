from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate
from pyow.utils import of_type, deep_eq


class SetPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(set, context)

    def size(self, size: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to have size `{size}`, got `{len(value)}`',
            'validator': lambda value: len(value) == size
        })

    def max_size(self, max_size: int) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to have maximum size of `{max_size}`, got `{len(value)}`',
            'validator': lambda value: len(value) <= max_size
        })

    def has(self, elements: set) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to have items {elements}',
            'validator': lambda zet: elements.issubset(zet)
        })

    def has_any(self, elements: set):
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to have any items {elements}',
            'validator': lambda zet: any(el in zet for el in elements)
        })

    def of_type(self, predicate: Predicate) -> Predicate:
        errors = []
        return self.add_validator({
            'message': lambda value, result=None: ''.join(errors),
            'validator': lambda value: of_type(value, predicate, errors)
        })

    def deep_equal(self, set_for_comparison: set) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to deep equal `{set_for_comparison}`, got `{value}`',
            'validator': lambda value: deep_eq(value, set_for_comparison)
        })

    @property
    def empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set to be empty, got `{value}`',
            'validator': lambda value: len(value) == 0
        })

    @property
    def non_empty(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected set not to be empty, got `{value}`',
            'validator': lambda value: len(value) > 0
        })
