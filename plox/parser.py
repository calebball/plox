from typing import List

from attr import define, field

from plox.cli import Plox
from plox.errors import LoxParseError
from plox.expressions import Assign, Binary, Expr, Grouping, Literal, Unary, Variable
from plox.statements import Block, Expression, If, Print, Stmt, Var
from plox.tokens import Token, TokenType


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
            statements.append(self.declaration())
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

    def error(self, token: Token, message: str) -> LoxParseError:
        Plox.error(token.line, message, token)
        return LoxParseError(token, message)

    def synchronise(self):
        self.advance()
        while not self.is_at_end:
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

    def declaration(self) -> Stmt:
        """Parse the next declaration from the token stream.

        This method implements the rule
            declaration -> varDecl
                        |  statement
        """
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()

        except LoxParseError:
            self.synchronise()

    def var_declaration(self) -> Stmt:
        """Parse the next variable declaration from the token stream.

        This method implements the rule
            varDecl -> identifier ("=" expression)? ";"
        """
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initialiser = None
        if self.match(TokenType.EQUAL):
            initialiser = self.expression()

        stmt = Var(name, initialiser)
        self.consume(TokenType.SEMICOLON, "Expect ';' after declaration.")
        return stmt

    def statement(self) -> Stmt:
        """Parse the next statement from the token stream.

        This method implements the rule
            statement   -> exprStmt
                        |  ifStmt
                        |  printStmt
                        |  block

        The block branch wraps the list of statements in a Block object in this
        method, which is to keep a bit of flexibility later on.
        """
        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())

        return self.expression_statement()

    def if_statement(self) -> If:
        """Parse the contents of an if statement from the token stream.

        This method implements the rule
            ifStmt -> "if" "(" expression ")" statement ( "else" statement )? ;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self) -> Print:
        """Parse the contents of a print statement from the token stream.

        This method implements the rule
            printStmt -> "print" expression ";"
        """
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def block(self) -> List[Stmt]:
        """Parse the contents of a block statement from the token stream.

        This method implements the rule
            block -> "{" declaration "}"

        Mostly, at least. We expect the left brace to have been consumed from
        the stream at this point.
        """
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end:
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

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
            expression -> assignment
        """
        return self.assignment()

    def assignment(self) -> Expr:
        """Parse an assignment expression from the token stream.

        This method implements the rule
            assignment  -> IDENTIFIER "=" assignment
                        |  equality
        """
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            Plox.error(equals.line, "Invalid assignment target.", equals)

        return expr

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
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        raise self.error(self.peek(), "Expect expression.")
