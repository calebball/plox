from typing import Any, Dict, List, Optional

from attr import define, field

from plox.errors import LoxRuntimeError
from plox.function import LoxFunction
from plox.tokens import Token


@define
class LoxInstance:
    klass: "LoxClass"
    fields: Dict[str, Any] = field(factory=dict)

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self.klass.name} instance"


@define
class LoxClass:
    name: str
    methods: Dict[str, LoxFunction]

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> LoxInstance:
        return LoxInstance(self)

    def arity(self) -> int:
        return 0

    def find_method(self, name: str) -> Optional[LoxFunction]:
        return self.methods.get(name)

    def __str__(self) -> str:
        return self.name
