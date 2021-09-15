from typing import List

from attr import define, field

from plox.cli import Plox
from plox.errors import LoxParseError
from plox.expressions import (
    Assign,
    Binary,
    Call,
    Expr,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from plox.statements import Block, Expression, Function, If, Print, Return, Stmt, Var, While
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
            declaration -> funDecl
                        |  varDecl
                        |  statement
        """
        try:
            if self.match(TokenType.FUN):
                return self.function("function")
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
                        |  forStmt
                        |  ifStmt
                        |  printStmt
                        |  returnStmt
                        |  whileStmt
                        |  block

        The block branch wraps the list of statements in a Block object in this
        method, which is to keep a bit of flexibility later on.
        """
        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())

        return self.expression_statement()

    def for_statement(self) -> Stmt:
        """Parse a for statement from the token stream.

        The statement is desugared into the equivalent while loop form. I.e. we
        translate
            for (init; cond; incr) { body; }
        into
            init;
            while (cond) {
                body;
                incr;
            }

        This method implements the rule
            forStmt -> "for" "(" ( varDecl | exprStmt | ";" )
                        expression? ";" expression? ")" statement;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(TokenType.SEMICOLON):
            initialiser = None
        elif self.match(TokenType.VAR):
            initialiser = self.var_declaration()
        else:
            initialiser = self.expression_statement()

        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = Literal(True)
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        else:
            increment = None

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after increment.")

        body = self.statement()
        if increment is not None:
            body = Block([body, Expression(increment)])
        body = While(condition, body)
        if initialiser is not None:
            body = Block([initialiser, body])
        return body

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

    def return_statement(self) -> Return:
        """Parse a return statement from the token stream.

        This method implements the rule
            returnStmt -> "return" expression ";"
        """
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def while_statement(self) -> While:
        """Parse the a while statement from the token stream.

        This method implements the rule
            whileStmt -> "while" "(" expression ")" statement ;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

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

    def function(self, kind: str) -> Stmt:
        """Parse a function definition from the token stream.

        This method implements the rule
            function -> IDENTIFIER "(" parameters? ")" block ;
        """
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(
                self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

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
                        |  logic_or
        """
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            Plox.error(equals.line, "Invalid assignment target.", equals)

        return expr

    def logic_or(self) -> Expr:
        """parse a logical or operator from the token stream.

        this method implements the rule
            logic_or -> logic_and ( "or" logic_and )* ;
        """
        expr = self.logic_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

    def logic_and(self) -> Expr:
        """parse a logical or operator from the token stream.

        this method implements the rule
            logic_and -> equality ( "or" equality )* ;
        """
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

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
            unary -> ( "!" | "-" ) unary | call ;
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        """Parse a function call from the token stream.

        This method implements the rules
            call -> primary ( "(" arguments? ")" )* ;
            arguments -> expression ( "," expression )* ;
        """
        expr = self.primary()

        while self.match(TokenType.LEFT_PAREN):
            arguments = []

            if not self.check(TokenType.RIGHT_PAREN):
                while self.match(TokenType.COMMA):
                    if len(arguments) >= 255:
                        self.error(self.peek(), "Can't have more than 255 arguments.")
                    arguments.append(self.expression())

            paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
            expr = Call(expr, paren, arguments)

        return expr

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
