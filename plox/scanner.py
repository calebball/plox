from typing import List, Optional

from attr import define, Factory

from plox.cli import Plox
from plox.tokens import TokenType, Token


@define
class Scanner:
    source: str
    tokens: List[Token] = Factory(list)
    start: int = 0
    current: int = 0
    line: int = 1

    def scan_tokens(self):
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        # Characters that uniquely define a single token
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "/":
            self.add_token(TokenType.SLASH)
        elif c == "*":
            self.add_token(TokenType.STAR)

        # Characters which may generate a single character token or a
        # two-character token
        elif c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
        elif c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)

        else:
            Plox.error(self.line, "Unexpected character.")

    @property
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def match(self, char: str) -> bool:
        if self.is_at_end:
            return False
        if self.source[self.current] != char:
            return False
        self.current += 1
        return True

    def add_token(self, type: TokenType, literal: Optional[object] = None):
        self.tokens.append(
            Token(type, self.source[self.start : self.current], literal, self.line)
        )
