from abc import ABC, abstractmethod
from typing import Any

from attr import define

from plox.tokens import Token


class Expr:
    def accept(self, visitor: "ExprVisitor"):
        ...


@define
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_assign(self)


@define
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_binary(self)


@define
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_grouping(self)


@define
class Literal(Expr):
    value: Any

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_literal(self)


@define
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_logical(self)


@define
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_unary(self)


@define
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
    def visit_grouping(self, expr: Grouping):
        ...

    @abstractmethod
    def visit_literal(self, expr: Literal):
        ...

    @abstractmethod
    def visit_logical(self, expr: Logical):
        ...

    @abstractmethod
    def visit_unary(self, expr: Unary):
        ...

    @abstractmethod
    def visit_variable(self, expr: Variable):
        ...
