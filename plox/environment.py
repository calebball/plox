from typing import Any, Dict

from attr import define, field

from plox.errors import LoxRuntimeError
from plox.tokens import Token


@define
class Environment:
    values: Dict[str, Any] = field(factory=dict)

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
