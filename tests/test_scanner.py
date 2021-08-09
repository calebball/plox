import pytest
from hypothesis import given, strategies as st

from plox.scanner import Scanner
from plox.tokens import TokenType


@pytest.mark.parametrize("char, type", [
    ("(", TokenType.LEFT_PAREN),
    (")", TokenType.RIGHT_PAREN),
    ("{", TokenType.LEFT_BRACE),
    ("}", TokenType.RIGHT_BRACE),
    (",", TokenType.COMMA),
    (".", TokenType.DOT),
    ("-", TokenType.MINUS),
    ("+", TokenType.PLUS),
    (";", TokenType.SEMICOLON),
    ("/", TokenType.SLASH),
    ("*", TokenType.STAR),
])
def test_scanning_single_characters(char: str, type: TokenType):
    """Test that we can scan one of the tokens that can be identified uniquely
    from a single character.

    Arguments:
        char: a length 1 string containing the character we're scanning.
        type: the type of token we're expecting to scan.
    """
    tokens = Scanner(char).scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is type


@given(source=st.text("(){},.-+;/*"))
def test_scanning_single_character_sequences(source: str):
    """Test that scanning a source string containing only single character
    tokens returns a list of tokens with the length of the source string plus
    one (for the EOF token.)

    Arguments:
        source: the Lox source string to scan.
    """
    assert len(Scanner(source).scan_tokens()) == len(source) + 1
