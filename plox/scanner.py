from typing import Any, List, Optional

from attr import define, Factory

from plox.cli import Plox
from plox.tokens import TokenType, Token


def is_digit(char: str) -> bool:
    """Check if a one character string is a digit."""
    return ord("0") <= ord(char) <= ord("9")


def is_alpha(char: str) -> bool:
    """Check if a one character string is an alphabetic character or an
    undercore.
    """
    return (
        ord("a") <= ord(char) <= ord("z")
        or ord("A") <= ord(char) <= ord("Z")
        or ord(char) == ord("_")
    )


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "it": TokenType.IT,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


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

        # Check for a comment
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end:
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)

        # Discard whitespace
        elif c in ["\t", " "]:
            pass
        elif c == "\n":
            self.line += 1

        # Literal tokens
        elif c == '"':
            self.string()
        elif is_digit(c):
            self.number()

        elif is_alpha(c):
            self.identifier()

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

    def peek(self) -> str:
        if self.is_at_end:
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end:
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end:
            Plox.error(self.line, "Unterminated string.")
            return

        # Consume the closing " character
        self.advance()
        self.add_token(
            TokenType.STRING, literal=self.source[self.start + 1 : self.current - 1]
        )

    def number(self):
        while is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and is_digit(self.peek_next()):
            self.advance()

            while is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def identifier(self):
        while is_alpha(self.peek()) or is_digit(self.peek()):
            self.advance()

        self.add_token(
            keywords.get(self.source[self.start : self.current], TokenType.IDENTIFIER)
        )

    def add_token(self, type: TokenType, literal: Optional[Any] = None):
        self.tokens.append(
            Token(type, self.source[self.start : self.current], literal, self.line)
        )
