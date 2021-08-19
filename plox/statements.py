from abc import ABC, abstractmethod

from attr import define

from plox.expressions import Expr
from plox.tokens import Token


class Stmt:
    def accept(self, visitor: "StmtVisitor"):
        ...


@define
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_expression(self)


@define
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_print(self)


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression(self, expr: Expression):
        ...

    @abstractmethod
    def visit_print(self, expr: Print):
        ...
