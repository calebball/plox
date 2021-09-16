from typing import Any, ClassVar, Dict, List

from attr import define, field

from plox.classes import LoxClass, LoxInstance
from plox.cli import Plox
from plox.environment import Environment, standard_global_environment
from plox.errors import LoxRuntimeError, ReturnException
from plox.expressions import (
    Assign,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Unary,
    Variable,
)
from plox.function import LoxFunction
from plox.statements import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    StmtVisitor,
    Var,
    While,
)
from plox.tokens import Token, TokenType


@define
class Interpreter(ExprVisitor, StmtVisitor):
    globals: ClassVar[Environment] = standard_global_environment()
    environment: Environment = field()
    locals: Dict[Expr, int] = field(factory=dict)

    @environment.default
    def _default_to_global_environment(self):
        return self.globals

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

    def visit_class(self, stmt: Class) -> None:
        self.environment.define(stmt.name.lexeme, None)
        cls = LoxClass(stmt.name.lexeme)
        self.environment.assign(stmt.name, cls)

    def visit_expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)

        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return(self, stmt: Return) -> None:
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_while(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_block(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_assign(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        depth = self.locals.get(expr)
        if depth is not None:
            self.environment.assign_at(depth, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
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

    def visit_call(self, expr: Call) -> Any:
        callee = self.evaluate(expr.callee)

        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if not (hasattr(callee, "call") and callable(callee.call)):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_get(self, expr: Get) -> Any:
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping(self, expr: Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_literal(self, expr: Literal) -> Any:
        return expr.value

    def visit_variable(self, expr: Variable) -> Any:
        return self.look_up_variable(expr.name, expr)

    def visit_set(self, expr: Set) -> Any:
        obj = self.evaluate(expr.obj)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

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

    def look_up_variable(self, name: Token, expr: Expr) -> Any:
        depth = self.locals.get(expr)
        if depth is not None:
            return self.environment.get_at(depth, name.lexeme)
        return self.globals.get(name)

    def check_number_operands(self, operator: Token, *operands: List[Any]) -> None:
        if any(not isinstance(operand, float) for operand in operands):
            if len(operands) > 1:
                raise LoxRuntimeError(operator, "Operands must be numbers.")
            else:
                raise LoxRuntimeError(operator, "Operand must be a number.")

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

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
