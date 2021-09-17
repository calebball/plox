from abc import ABC, abstractmethod
from typing import List, Optional

from attr import define

from plox.expressions import Expr, Variable
from plox.tokens import Token


class Stmt:
    def accept(self, visitor: "StmtVisitor"):
        ...


@define
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_block(self)


@define
class Class(Stmt):
    name: Token
    superclass: Variable
    methods: List["Function"]

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_class(self)


@define
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_expression(self)


@define
class Function(Stmt):
    name: Token
    params: List[Token]
    body: Stmt

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_function(self)


@define
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_if(self)


@define
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_print(self)


@define
class Return(Stmt):
    keyword: Token
    value: Expr

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_return(self)


@define
class Var(Stmt):
    name: Token
    initialiser: Optional[Expr]

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_var(self)


@define
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: "StmtVisitor"):
        return visitor.visit_while(self)


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block(self, expr: Block):
        ...

    @abstractmethod
    def visit_class(self, expr: Class):
        ...

    @abstractmethod
    def visit_expression(self, expr: Expression):
        ...

    @abstractmethod
    def visit_function(self, expr: Function):
        ...

    @abstractmethod
    def visit_if(self, expr: If):
        ...

    @abstractmethod
    def visit_print(self, expr: Print):
        ...

    @abstractmethod
    def visit_return(self, expr: Return):
        ...

    @abstractmethod
    def visit_var(self, expr: Var):
        ...

    @abstractmethod
    def visit_while(self, expr: While):
        ...
