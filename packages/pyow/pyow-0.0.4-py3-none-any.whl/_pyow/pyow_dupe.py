from typing import Any, Callable

from pyow.types import Predicate


class pyow_dupe:
    @staticmethod
    def __call__(value: Any, predicate: Predicate) -> Callable:
        return getattr(predicate, 'test')(value, pyow_dupe)


pyow_dupe = pyow_dupe()
