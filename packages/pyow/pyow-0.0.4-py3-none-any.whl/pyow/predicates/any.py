from typing import Any, List, Callable

from pyow import ArgumentError
from pyow.predicates.base_predicate import BasePredicate
from pyow.types import Predicate


class AnyPredicate(BasePredicate):
    def __init__(self, predicates: List[Predicate]):
        self.predicates: List[Predicate] = predicates

    def test(self, value: Any, pyow: Callable) -> None:
        errors: List[str] = [
            'Any predicate failed with the following errors'
        ]

        for predicate in self.predicates:
            try:
                pyow(value, predicate)
                return
            except ArgumentError as e:
                errors.append(f' - {e.message}')

        joined_errors = '\n'.join(errors)
        raise ArgumentError(f"{joined_errors}", pyow)
