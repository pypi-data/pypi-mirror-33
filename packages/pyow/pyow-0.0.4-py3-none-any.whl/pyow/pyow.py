from typing import Callable, Any

from pyow.predicates.dict import DictPredicate
from pyow.predicates.error import ErrorPredicate
from pyow.predicates.list import ListPredicate
from pyow.predicates.number import NumberPredicate
from pyow.predicates.set import SetPredicate
from pyow.predicates.string import StringPredicate
from pyow.predicates.boolean import BooleanPredicate
from pyow.types import Predicate


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
    def error(self):
        return ErrorPredicate()

    @staticmethod
    def __call__(value: Any, predicate: Predicate) -> Callable:
        return getattr(predicate, 'test')(value, pyow)


pyow = pyow()
