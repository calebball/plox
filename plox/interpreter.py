from typing import Any, List

from attr import define, field

from plox.cli import Plox
from plox.environment import Environment
from plox.errors import LoxRuntimeError
from plox.expressions import Binary, Expr, ExprVisitor, Grouping, Literal, Unary, Variable
from plox.statements import Expression, Print, Stmt, StmtVisitor, Var
from plox.tokens import Token, TokenType


@define
class Interpreter(ExprVisitor, StmtVisitor):
    environment: Environment = field(factory=Environment)

    def interpret(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)

        except LoxRuntimeError as exc:
            Plox.runtime_error(exc)

    def visit_var(self, stmt: Var) -> None:
        value = None
        if stmt.initialiser is not None:
            value = self.evaluate(stmt.initialiser)

        self.environment.define(stmt.name.lexeme, value)

    def visit_expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_binary(self, expr: Binary) -> Any:
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

    def visit_grouping(self, expr: Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_literal(self, expr: Literal) -> Any:
        return expr.value

    def visit_variable(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def visit_unary(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.operator.type is TokenType.MINUS:
            self.check_number_operands(expr.operator, right)
            return -float(right)

        if expr.operator.type is TokenType.BANG:
            return not self.is_truthy(right)

    def execute(self, stmt: Stmt) -> None:
        return stmt.accept(self)

    def evaluate(self, expr: Expr) -> Any:
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
