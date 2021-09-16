import enum
from typing import Dict, List

from attr import define, field

from plox.cli import Plox
from plox.expressions import (
    Assign,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from plox.interpreter import Interpreter
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
from plox.tokens import Token


class FunctionType(enum.Enum):
    NONE = enum.auto()
    FUNCTION = enum.auto()


@define
class Resolver(ExprVisitor, StmtVisitor):
    interpreter: Interpreter
    scopes: List[Dict[str, bool]] = field(factory=list)
    current_function: FunctionType = FunctionType.NONE

    def visit_block(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_class(self, stmt: Class) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

    def visit_expression(self, stmt: Expression) -> None:
        self.resolve_expression(stmt.expression)

    def visit_function(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if(self, stmt: If) -> None:
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_statement(stmt.else_branch)

    def visit_print(self, stmt: Print) -> None:
        self.resolve_expression(stmt.expression)

    def visit_return(self, stmt: Return) -> None:
        if self.current_function is FunctionType.NONE:
            Plox.error(
                stmt.keyword.line, "Can't return from top-level code.", stmt.keyword
            )
        if stmt.value is not None:
            self.resolve_expression(stmt.value)

    def visit_var(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initialiser is not None:
            self.resolve_expression(stmt.initialiser)
        self.define(stmt.name)

    def visit_while(self, stmt: While) -> None:
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.body)

    def visit_assign(self, expr: Assign) -> None:
        self.resolve_expression(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary(self, expr: Binary) -> None:
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_call(self, expr: Call) -> None:
        self.resolve_expression(expr.callee)
        for arg in expr.arguments:
            self.resolve_expression(arg)

    def visit_grouping(self, expr: Grouping) -> None:
        self.resolve_expression(expr.expression)

    def visit_literal(self, expr: Literal) -> None:
        pass

    def visit_logical(self, expr: Logical) -> None:
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_unary(self, expr: Unary) -> None:
        self.resolve_expression(expr.right)

    def visit_variable(self, expr: Variable) -> None:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            Plox.error(
                expr.name.line,
                "Can't read local variable in its own initializer.",
                expr.name,
            )
        self.resolve_local(expr, expr.name)

    def resolve(self, statements: List[Stmt]) -> None:
        for stmt in statements:
            self.resolve_statement(stmt)

    def resolve_statement(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve_expression(self, expr: Expr) -> None:
        expr.accept(self)

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for depth, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                return self.interpreter.resolve(expr, depth)

    def resolve_function(self, stmt: Function, function_type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = function_type
        self.begin_scope()

        for param in stmt.params:
            self.declare(param)
            self.define(param)
        self.resolve(stmt.body)

        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if self.scopes:
            current_scope = self.scopes[-1]
            if name.lexeme in current_scope:
                Plox.error(
                    name.line, "Already a variable with this name in this scope.", name
                )
            current_scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if self.scopes:
            self.scopes[-1][name.lexeme] = True
