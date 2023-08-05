from typing import Callable

from pyow import pyow
from pyow.exceptions import ArgumentMismatchError


class validate(object):
    def __init__(self, *validators):
        self.validators = list(validators)

    def __call__(self, f) -> Callable:
        def wrapped_f(*args, **kwargs) -> Callable:
            no_args = len(args) + 1 if kwargs else len(args)

            if no_args != len(self.validators):
                raise ArgumentMismatchError(
                    f'Function got `{len(args) + len(kwargs)}` arguments, expected `{len(self.validators)}`', self
                )

            for i, arg in enumerate(args):
                pyow(arg, self.validators.pop(i))

            if kwargs:
                pyow(kwargs, self.validators.pop())
            f(*args, **kwargs)

        return wrapped_f
