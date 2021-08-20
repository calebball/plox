import enum
from typing import Optional, Union

from attr import define, field


class TokenType(enum.Enum):
    # Single character tokens
    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()
    LEFT_BRACE = enum.auto()
    RIGHT_BRACE = enum.auto()
    COMMA = enum.auto()
    DOT = enum.auto()
    MINUS = enum.auto()
    PLUS = enum.auto()
    SEMICOLON = enum.auto()
    SLASH = enum.auto()
    STAR = enum.auto()

    # One or two character tokens
    BANG = enum.auto()
    BANG_EQUAL = enum.auto()
    EQUAL = enum.auto()
    EQUAL_EQUAL = enum.auto()
    GREATER = enum.auto()
    GREATER_EQUAL = enum.auto()
    LESS = enum.auto()
    LESS_EQUAL = enum.auto()

    # Literals
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()

    # Keywords
    AND = enum.auto()
    CLASS = enum.auto()
    ELSE = enum.auto()
    FALSE = enum.auto()
    FUN = enum.auto()
    FOR = enum.auto()
    IT = enum.auto()
    NIL = enum.auto()
    OR = enum.auto()
    PRINT = enum.auto()
    RETURN = enum.auto()
    SUPER = enum.auto()
    THIS = enum.auto()
    TRUE = enum.auto()
    VAR = enum.auto()
    WHILE = enum.auto()

    EOF = enum.auto()


@define
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[Union[str, float]]
    line: int = field(converter=int)

    def __str__(self):
        truthy_attributes = [
            attr
            for attr in [self.line, self.type.name, self.lexeme, self.literal]
            if attr
        ]
        return " ".join(map(str, truthy_attributes))

    @classmethod
    def from_str(cls, string: str):
        start = 0
        current = 0

        while not string[current].isspace():
            current = current + 1

        line = int(string[start:current])

        current = current + 1
        start = current

        while not string[current].isspace():
            current = current + 1

        type = TokenType[string[start:current]]

        start = current + 1
        lexeme = string[start:-1]

        if not lexeme:
            return cls(type, "", None, line)

        if type is TokenType.TRUE:
            return cls(type, "true", True, line)

        if type is TokenType.FALSE:
            return cls(type, "false", False, line)

        if type is TokenType.NUMBER:
            return cls(type, lexeme, float(lexeme), line)

        if type is TokenType.STRING:
            return cls(type, f'"{lexeme}"', lexeme, line)

        return cls(type, lexeme, None, line)
