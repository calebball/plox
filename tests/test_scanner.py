import functools

import pytest
from hypothesis import given, strategies as st

from plox.cli import Plox
from plox.scanner import Scanner
from plox.tokens import TokenType


def no_errors(test_function):
    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        try:
            test_function(*args, **kwargs)
        except Exception as exc:
            Plox.HAD_ERROR = False
            raise exc
        else:
            had_error = Plox.HAD_ERROR
            Plox.HAD_ERROR = False
            assert not had_error
    return wrapper


def causes_error(test_function):
    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        try:
            test_function(*args, **kwargs)
        except Exception as exc:
            Plox.HAD_ERROR = False
            raise exc
        else:
            had_error = Plox.HAD_ERROR
            Plox.HAD_ERROR = False
            assert had_error
    return wrapper


@pytest.mark.parametrize(
    "char, type",
    [
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
    ],
)
@no_errors
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
@no_errors
def test_scanning_single_character_sequences(source: str):
    """Test that scanning a source string containing only single character
    tokens returns a list of tokens with the length of the source string plus
    one (for the EOF token.)

    Arguments:
        source: the Lox source string to scan.
    """
    assert len(Scanner(source).scan_tokens()) == len(source) + 1


@given(source=st.text("@#^", min_size=1))
@causes_error
def test_lexical_error(source: str):
    """Test that the scanner safely handles a string comprised of characters
    that aren't used in the Lox language.

    The scanner needs to discard each character and continue scanning, so we
    should end up with a list of tokens that only contains EOF. We also need to
    signal the error.

    Arguments:
        source: the Lox source string to scan.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].type is TokenType.EOF
