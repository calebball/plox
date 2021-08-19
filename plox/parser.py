from typing import List, Optional

from attr import define, field

from plox.cli import Plox
from plox.expressions import Binary, Expr, Grouping, Literal, Unary
from plox.statements import Expression, Print, Stmt
from plox.tokens import Token, TokenType


class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        super(ParseError, self).__init__(message)


@define
class Parser:
    tokens: List[Token]
    current: int = field(default=0, init=False)

    def parse(self) -> List[Stmt]:
        """Parse the token stream using a recursive descent parser.

        This method implements the rule
            program -> statement* EOF

        Returns:
            The list of statements parsed out of the token stream.
        """
        statements = []
        while not self.is_at_end:
            statements.append(self.statement())
        return statements

    @property
    def is_at_end(self):
        return self.peek().type is TokenType.EOF

    def advance(self) -> Token:
        if not self.is_at_end:
            self.current += 1

        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end:
            return False

        return self.peek().type is type

    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        Plox.error(token.line, message, token)
        return ParseError(token, message)

    def synchronise(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type is TokenType.SEMICOLON:
                return

            if self.peek().type in [
                TokenType.CLASS,
                TokenType.FOR,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
                TokenType.VAR,
                TokenType.WHILE,
            ]:
                return

        self.advance()

    def statement(self) -> Stmt:
        """Parse the next statement from the token stream.

        This method implements the rule
            statement   -> exprStmt
                        |  printStmt
        """
        if self.match(TokenType.PRINT):
            return self.print_statement()

        return self.expression_statement()

    def print_statement(self) -> Print:
        """Parse the contents of a print statement from the token stream.

        This method implements the rule
            printStmt -> "print" expression ";"
        """
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self) -> Expression:
        """Parse the contents of an expression statement from the token stream.

        This method implements the rule
            exprStmt -> expression ";"
        """
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(value)

    def expression(self) -> Expr:
        """Parse the next expression in the token stream.

        This method implements the rule
            expression -> equality
        """
        return self.equality()

    def equality(self) -> Expr:
        """Parse an equality expression from the token stream.

        This method implements the rule
            equality -> comparison (("==" | "!=") comparison)*
        """
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        """Parse a comparison expression from the token stream.

        This method implements the rule
            comparison -> term ((">", ">=", "<", "<=" term)*
        """
        expr = self.term()
        while self.match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        """Parse an addition expression from the token stream.

        This method implements the rule
            term -> factor (("+", "-") factor)*
        """
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        """Parse a multiplication expression from the token stream.

        This method implements the rule
            factor -> unary (("*", "/") unary)*
        """
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        """Parse a unary expression from the token stream.

        This method implements the rule
            unary -> ("!", "-")* primary
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        """Parse a primary expression from the front of the token stream.

        This method implements the rule
            primary -> nil | bool | number | string | grouping
        """
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")
