from typing import Any, List

from attr import define


@define
class LoxInstance:
    klass: "LoxClass"

    def __str__(self) -> str:
        return f"{self.klass.name} instance"


@define
class LoxClass:
    name: str

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> LoxInstance:
        return LoxInstance(self)

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return self.name
