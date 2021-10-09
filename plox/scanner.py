from io import TextIOBase
from typing import List, Optional

from plox.cli import Plox
from plox.io import PeekableTextIO
from plox.tokens import TokenType, Token


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
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


def return_token(token_type: TokenType):
    def return_token_closure(char, stream):
        return Token(token_type, char, None, stream.line)
    return return_token_closure


def select_with_peek(peek_char: str, match_token: TokenType, no_match_token: TokenType):
    def select_with_peek_closure(char, stream):
        if stream.match(peek_char):
            return Token(match_token, "".join([char, peek_char]), None, stream.line)
        return Token(no_match_token, char, None, stream.line)
    return select_with_peek_closure


def scan_slash_or_comment(char: str, stream: PeekableTextIO) -> Optional[Token]:
    if stream.match("/"):
        while stream.peek() and stream.peek() != "\n":
            stream.advance()
        return None

    return Token(TokenType.SLASH, "/", None, stream.line)


def consume_space(char, stream):
    while stream.peek() in [" ", "\t", "\n"]:
        stream.advance()


def scan_string(char: str, stream: PeekableTextIO) -> Optional[Token]:
    chars = []
    while stream.peek() and stream.peek() != '"':
        chars.append(stream.advance())
    if not stream.peek():
        Plox.error(stream.line, "Unterminated string.")
        return None
    stream.advance()
    string = "".join(chars)
    return Token(TokenType.STRING, f'"{string}"', string, stream.line)


def scan_number_or_identifier(char: str, stream: PeekableTextIO) -> Optional[Token]:
    if char.isdigit():
        chars = [char]
        while stream.peek().isdigit():
            chars.append(stream.advance())

        if stream.peek() == "." and stream.peek(1).isdigit():
            chars.append(stream.advance())
            while stream.peek().isdigit():
                chars.append(stream.advance())

        string = "".join(chars)
        return Token(TokenType.NUMBER, string, float(string), stream.line)

    if char.isalpha() or char == "_":
        chars = [char]
        while stream.peek().isalnum() or stream.peek() == "_":
            chars.append(stream.advance())

        lexeme = "".join(chars)
        token_type = keywords.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, None, stream.line)

    Plox.error(stream.line, "Unexpected character.")
    return None


scanners = {
    "(": return_token(TokenType.LEFT_PAREN),
    ")": return_token(TokenType.RIGHT_PAREN),
    "{": return_token(TokenType.LEFT_BRACE),
    "}": return_token(TokenType.RIGHT_BRACE),
    ",": return_token(TokenType.COMMA),
    ".": return_token(TokenType.DOT),
    "-": return_token(TokenType.MINUS),
    "+": return_token(TokenType.PLUS),
    ";": return_token(TokenType.SEMICOLON),
    "*": return_token(TokenType.STAR),
    "!": select_with_peek("=", TokenType.BANG_EQUAL, TokenType.BANG),
    "=": select_with_peek("=", TokenType.EQUAL_EQUAL, TokenType.EQUAL),
    ">": select_with_peek("=", TokenType.GREATER_EQUAL, TokenType.GREATER),
    "<": select_with_peek("=", TokenType.LESS_EQUAL, TokenType.LESS),
    "/": scan_slash_or_comment,
    "\t": consume_space,
    " ": consume_space,
    "\n": consume_space,
    '"': scan_string,
}


def scan_tokens(source: TextIOBase) -> List[Token]:
    stream = PeekableTextIO(source, 2)
    tokens = []

    while (char := stream.advance()):
        scanning_function = scanners.get(char, scan_number_or_identifier)
        if (token := scanning_function(char, stream)):
            tokens.append(token)

    tokens.append(Token(TokenType.EOF, "", None, stream.line))
    return tokens
