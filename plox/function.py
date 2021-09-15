from typing import Any, List

from attr import define

from plox.errors import ReturnException
from plox.environment import Environment
from plox.statements import Function


@define
class LoxFunction:
    declaration: Function
    closure: Environment

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> None:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as exc:
            return exc.value

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
