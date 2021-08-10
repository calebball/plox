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
        string_parts = string.split()
        line = string_parts[0]
        type = TokenType[string_parts[1]]

        if not len(string_parts) > 2:
            return cls(type, "", None, line)

        lexeme = string_parts[2]

        if not len(string_parts) > 3:
            return cls(type, lexeme, None, line)

        literal = string_parts[3]

        if type is TokenType.NUMBER:
            literal = float(literal)

        return cls(type, lexeme, literal, line)
