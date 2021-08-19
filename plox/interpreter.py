from typing import Any, List

from plox.expressions import ExprVisitor, Binary, Expr, Grouping, Literal, Unary
from plox.cli import Plox
from plox.errors import LoxRuntimeError
from plox.tokens import Token, TokenType


class Interpreter(ExprVisitor):
    def interpret(self, expr: Expr):
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))

        except LoxRuntimeError as exc:
            Plox.runtime_error(exc)

    def visit_binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type is TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        if expr.operator.type is TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        if expr.operator.type is TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)

        if expr.operator.type is TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        if expr.operator.type is TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)

        if expr.operator.type is TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)

        if expr.operator.type is TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left + right)

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise LoxRuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )

        if expr.operator.type is TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)

        if expr.operator.type is TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        if expr.operator.type is TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)

    def visit_grouping(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal(self, expr: Literal):
        return expr.value

    def visit_unary(self, expr: Unary):
        right = self.evaluate(expr.right)

        if expr.operator.type is TokenType.MINUS:
            self.check_number_operands(expr.operator, right)
            return -float(right)

        if expr.operator.type is TokenType.BANG:
            return not self.is_truthy(right)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def is_equal(self, left: Any, right: Any) -> bool:
        return left == right

    def check_number_operands(self, operator: Token, *operands: List[Any]) -> None:
        if any(not isinstance(operand, float) for operand in operands):
            raise LoxRuntimeError(operator, "Operand must be a number.")

    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(obj)