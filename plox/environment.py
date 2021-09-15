import time
from typing import Any, Dict, Optional

from attr import define, field

from plox.callables import LoxCallable
from plox.errors import LoxRuntimeError
from plox.tokens import Token


@define
class Environment:
    enclosing: Optional["Environment"] = field(default=None)
    values: Dict[str, Any] = field(init=False, factory=dict)

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def ancestor(self, depth: int) -> "Environment":
        env = self
        for _ in range(depth):
            env = env.enclosing
        return env

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, depth: int, name: str) -> Any:
        return self.ancestor(depth).values[name]

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, depth: int, name: Token, value: Any) -> None:
        self.ancestor(depth).values[name.lexeme] = value


def standard_global_environment() -> Environment:
    env = Environment()
    env.define(
        "clock",
        LoxCallable(
            arity=lambda: 0,
            call=lambda interpreter, arguments: time.time(),
            as_string=lambda: "<native fn>",
        ),
    )
    return env
