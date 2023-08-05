from typing import Callable, Any, List

from pyow.exceptions import ArgumentError
from pyow.predicates.any import AnyPredicate
from pyow.predicates.dict import DictPredicate
from pyow.predicates.error import ErrorPredicate
from pyow.predicates.list import ListPredicate
from pyow.predicates.number import NumberPredicate
from pyow.predicates.set import SetPredicate
from pyow.predicates.string import StringPredicate
from pyow.predicates.boolean import BooleanPredicate
from pyow.predicates.tuple import TuplePredicate
from pyow.types import Predicate

name = "pyow"


class pyow:
    @property
    def string(self):
        return StringPredicate()

    @property
    def boolean(self):
        return BooleanPredicate()

    @property
    def list(self):
        return ListPredicate()

    @property
    def number(self):
        return NumberPredicate()

    @property
    def set(self):
        return SetPredicate()

    @property
    def dict(self):
        return DictPredicate()

    @property
    def tuple(self):
        return TuplePredicate()

    @property
    def error(self):
        return ErrorPredicate()

    @staticmethod
    def any(*predicates: List[Predicate]) -> Predicate:
        return AnyPredicate(predicates)

    @staticmethod
    def __call__(value: Any, predicate: Predicate) -> Callable:
        return getattr(predicate, 'test')(value, pyow)

    @staticmethod
    def is_valid(value, predicate) -> bool:
        try:
            pyow(value, predicate)
            return True
        except ArgumentError:
            return False

    @staticmethod
    def create(predicate: Predicate) -> Callable:
        return lambda value: pyow(value, predicate)


pyow = pyow()
