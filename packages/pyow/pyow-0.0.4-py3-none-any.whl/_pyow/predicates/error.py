from typing import Any

from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate


class ErrorPredicate(BasePredicate):
    def __init__(self, context: Any=None):
        super().__init__(Exception, context)

    def name(self, expected: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected error to have name `{expected}`, got `{value.__class__.__name__}`',
            'validator': lambda value: value.__class__.__name__ == expected
        })

    def message(self, expected: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected error message to be `{expected}`, got `{value.__str__()}`',
            'validator': lambda value: value.__str__() == expected
        })

    def message_includes(self, expected: str) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f'Expected error message to include `{expected}`, got `{value.__str__()}`',
            'validator': lambda value: expected in value.__str__()
        })

    def has_keys(self, keys: list) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected error to have keys `{', '.join([str(x) for x in keys])}`",
            'validator': lambda value: all(key in vars(value).keys() for key in keys)
        })

    def instance_of(self, instance: any) -> Predicate:
        return self.add_validator({
            'message': lambda value, result=None: f"Expected error `{value.__class__.__name__}` to be instance of `{instance.__name__}` ",
            'validator': lambda value: isinstance(value, instance)
        })

