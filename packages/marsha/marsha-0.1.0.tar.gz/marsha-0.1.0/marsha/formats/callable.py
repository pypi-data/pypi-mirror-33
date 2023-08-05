import typing
from .any import Any


class Callable(Any):
    model_type = typing.Callable

    @staticmethod
    def dump(fn):
        return fn()
