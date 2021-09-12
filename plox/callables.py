from typing import Callable

from attr import define


@define
class LoxCallable:
    arity: Callable[[], int]
    call: Callable
    as_string: Callable[[], str]

    def __str__(self) -> str:
        return self.as_string()
