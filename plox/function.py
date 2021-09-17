from typing import Any, List

from attr import define

from plox.errors import ReturnException
from plox.environment import Environment
from plox.statements import Function


@define
class LoxFunction:
    declaration: Function
    closure: Environment
    is_initialiser: bool

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initialiser)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> None:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as exc:
            if self.is_initialiser:
                return self.closure.get_at(0, "this")
            return exc.value

        if self.is_initialiser:
            return self.closure.get_at(0, "this")

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
