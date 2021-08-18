from typing import Any

from plox.ast import AstVisitor, Binary, Expr, Grouping, Literal, Unary
from plox.tokens import TokenType


class Interpreter(AstVisitor):
    def visit_binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type is TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        if expr.operator.type is TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        if expr.operator.type is TokenType.GREATER:
            return float(left) > float(right)

        if expr.operator.type is TokenType.GREATER_EQUAL:
            return float(left) >= float(right)

        if expr.operator.type is TokenType.LESS:
            return float(left) < float(right)

        if expr.operator.type is TokenType.LESS_EQUAL:
            return float(left) <= float(right)

        if expr.operator.type is TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return float(left + right)

            if isinstance(left, str) and isinstance(right, str):
                return left + right

        if expr.operator.type is TokenType.MINUS:
            return float(left) - float(right)

        if expr.operator.type is TokenType.STAR:
            return float(left) * float(right)

        if expr.operator.type is TokenType.SLASH:
            return float(left) / float(right)

    def visit_grouping(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal(self, expr: Literal):
        return expr.value

    def visit_unary(self, expr: Unary):
        right = self.evaluate(expr.right)

        if expr.operator.type is TokenType.MINUS:
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
