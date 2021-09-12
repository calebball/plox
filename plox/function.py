from typing import Any, List

from attr import define

from plox.environment import Environment
from plox.statements import Function


@define
class LoxFunction:
    declaration: Function

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> None:
        environment = Environment(interpreter.globals)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        interpreter.execute_block(self.declaration.body, environment)

    def arity(self) -> int:
        return len(self.declaration.params)

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"
