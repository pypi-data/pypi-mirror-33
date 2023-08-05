from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate


class BooleanPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(bool, context)

    @property
    def true(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be True',
            'validator': lambda value: value is True,
        })

    @property
    def false(self) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected `{value}` to be False',
            'validator': lambda value: value is False,
        })
