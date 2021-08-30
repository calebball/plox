from typing import Any, List

from attr import define, field

from plox.cli import Plox
from plox.environment import Environment
from plox.errors import LoxRuntimeError
from plox.expressions import (
    Assign,
    Binary,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from plox.statements import Block, Expression, If, Print, Stmt, StmtVisitor, Var, While
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

    def visit_if(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)

        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_while(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_block(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_assign(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_logical(self, expr: Logical) -> Any:
        result = self.evaluate(expr.left)
        if (expr.operator.type is TokenType.AND and self.is_truthy(result)) or (
            expr.operator.type is TokenType.OR and not self.is_truthy(result)
        ):
            result = self.evaluate(expr.right)
        return result

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

    def execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment

            for stmt in statements:
                self.execute(stmt)

        finally:
            self.environment = previous

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def is_equal(self, left: Any, right: Any) -> bool:
        if isinstance(left, bool) or isinstance(right, bool):
            return left is right
        return left == right

    def check_number_operands(self, operator: Token, *operands: List[Any]) -> None:
        if any(not isinstance(operand, float) for operand in operands):
            if len(operands) > 1:
                raise LoxRuntimeError(operator, "Operands must be numbers.")
            else:
                raise LoxRuntimeError(operator, "Operand must be a number.")

    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"

        if obj is True:
            return "true"

        if obj is False:
            return "false"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(obj)
