from typing import Any, Dict, List

from attr import define, field

from plox.errors import LoxRuntimeError
from plox.tokens import Token


@define
class LoxInstance:
    klass: "LoxClass"
    fields: Dict[str, Any] = field(factory=dict)

    def get(self, name: Token) -> Any:
        try:
            return self.fields[name.lexeme]
        except KeyError:
            raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

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
