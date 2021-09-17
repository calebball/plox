from abc import ABC, abstractmethod
from typing import Any, List

from attr import define

from plox.tokens import Token


class Expr:
    def accept(self, visitor: "ExprVisitor"):
        ...


@define(eq=False)
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_assign(self)


@define(eq=False)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_binary(self)


@define(eq=False)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr]

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_call(self)


@define(eq=False)
class Get(Expr):
    obj: Expr
    name: Token

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_get(self)


@define(eq=False)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_grouping(self)


@define(eq=False)
class Literal(Expr):
    value: Any

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_literal(self)


@define(eq=False)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_logical(self)


@define(eq=False)
class Set(Expr):
    obj: Expr
    name: Token
    value: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_set(self)


@define(eq=False)
class This(Expr):
    keyword: Token

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_this(self)


@define(eq=False)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_unary(self)


@define(eq=False)
class Variable(Expr):
    name: Token

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_variable(self)


class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign(self, expr: Assign):
        ...

    @abstractmethod
    def visit_binary(self, expr: Binary):
        ...

    @abstractmethod
    def visit_call(self, expr: Call):
        ...

    @abstractmethod
    def visit_get(self, expr: Get):
        ...

    @abstractmethod
    def visit_grouping(self, expr: Grouping):
        ...

    @abstractmethod
    def visit_literal(self, expr: Literal):
        ...

    @abstractmethod
    def visit_logical(self, expr: Logical):
        ...

    @abstractmethod
    def visit_set(self, expr: Set):
        ...

    @abstractmethod
    def visit_this(self, expr: This):
        ...

    @abstractmethod
    def visit_unary(self, expr: Unary):
        ...

    @abstractmethod
    def visit_variable(self, expr: Variable):
        ...
