from abc import ABC, abstractmethod
from typing import Any

from attr import define

from plox.tokens import Token


class Expr:
    def accept(self, visitor: "ExprVisitor"):
        ...


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
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.visit_unary(self)


class ExprVisitor(ABC):
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
    def visit_unary(self, expr: Unary):
        ...
