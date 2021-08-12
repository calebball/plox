import functools
from collections import Counter

import pytest
from hypothesis import given, strategies as st

from plox.cli import Plox
from plox.scanner import keywords, Scanner
from plox.tokens import TokenType


def remove_whitespace(string: str) -> str:
    return "".join(string.split())


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


@given(source=st.text("\n\t (){},.-+;*"))
@no_errors
def test_scanning_single_character_sequences(source: str):
    """Test that scanning a source string containing only single character
    tokens returns a list of tokens with the length of the source string plus
    one (for the EOF token.)

    The allowed character set for the source string includes whitespace
    characters, because those should be ignored by the scanner. This means we
    can't just use the length of the string as the number of tokens, we need to
    count the number of non-whitespace characters.

    Arguments:
        source: the Lox source string to scan.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == len(remove_whitespace(source)) + 1
    assert max(token.line for token in tokens) == Counter(source)["\n"] + 1


@given(source=st.text("\n\t @#^", min_size=1).filter(lambda string: string.strip()))
@causes_error
def test_lexical_error(source: str):
    """Test that the scanner safely handles a string comprised of characters
    that aren't used in the Lox language.

    The scanner needs to discard each character and continue scanning, so we
    should end up with a list of tokens that only contains EOF. We also need to
    signal the error.

    The allowed character set for the source string includes whitespace
    characters, because those should be ignored by the scanner.

    Arguments:
        source: the Lox source string to scan.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].type is TokenType.EOF
    assert tokens[0].line == Counter(source)["\n"] + 1


@pytest.mark.parametrize(
    "source, type",
    [
        ("!", TokenType.BANG),
        ("!=", TokenType.BANG_EQUAL),
        ("=", TokenType.EQUAL),
        ("==", TokenType.EQUAL_EQUAL),
        (">", TokenType.GREATER),
        (">=", TokenType.GREATER_EQUAL),
        ("<", TokenType.LESS),
        ("<=", TokenType.LESS_EQUAL),
        ("/", TokenType.SLASH),
    ],
)
@no_errors
def test_scanning_one_or_two_char_lexeme(source: str, type: TokenType):
    """Test that we can scan a lexeme where the first character could either
    be a single token itself, or be the start of a two character token.

    Arguments:
        source: the Lox source string to scan.
        type: the type of token we're expecting to scan.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is type


@given(comment=st.text().filter(lambda string: "\n" not in string))
@no_errors
def test_scanning_comment(comment: str):
    """Test that the scanner will discard a line that begins with a comment
    token.

    Arguments:
        comment: a string to be used as a comment.
    """
    assert len(Scanner(f"//{comment}").scan_tokens()) == 1


@given(string=st.text().filter(lambda string: '"' not in string))
@no_errors
def test_scanning_strings(string: str):
    """Test that we can scan a (possibly multi-line) string.

    Lox doesn't allow any character escaping, so generating strings to feed
    into this test is easy.

    Arguments:
        string: the contents of a string to be scanned.
    """
    tokens = Scanner(f'"{string}"').scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is TokenType.STRING
    assert tokens[0].literal == string
    assert tokens[1].line == Counter(string)["\n"] + 1


@given(string=st.text().filter(lambda string: '"' not in string))
@causes_error
def test_scanning_unterminated_string(string: str):
    """Test that an error is generated when an unterminated comment is scanned.

    Arguments:
        string: the contents of a string to be scanned.
    """
    tokens = Scanner(f'"{string}').scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].type is TokenType.EOF
    assert tokens[0].line == Counter(string)["\n"] + 1


@given(
    number=st.floats(min_value=0, allow_nan=False, allow_infinity=False),
    decimal_places=st.integers(min_value=0, max_value=32),
)
@no_errors
def test_scanning_decimal_numbers(number: float, decimal_places: int):
    """Test that we can scan an appropriately formatted decimal number.

    Decimal numbers in Lox
    - must begin with a digit
    - must end with a digit

    Arguments:
        number: the number that we're going format and scan.
        decimal_places: the amount of decimal places to format the number with.
    """
    source = f"{number:.{decimal_places}f}"
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is TokenType.NUMBER
    assert tokens[0].literal == float(source)


@pytest.mark.parametrize(
    "source, type", [(keyword, token_type) for keyword, token_type in keywords.items()]
)
@no_errors
def test_scanning_keywords(source: str, type: TokenType):
    """Test that we can correctly scan a keyword of the Lox language.

    Arguments:
        source: the Lox source code string we're scanning.
        type: the type of token we're expecting to scan.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is type


@given(
    source=st.text(
        st.characters(
            whitelist_categories=("Ll", "Lu", "Nd"),
            whitelist_characters="_",
            max_codepoint=128,
        ),
        min_size=1,
    )
    .filter(lambda string: not (ord("0") <= ord(string[0]) <= ord("9")))
    .filter(lambda string: string not in keywords)
)
@no_errors
def test_scanning_identifiers(source: str):
    """Test that we can correctly scan a valid identifier.

    Arguments:
        source: the Lox source code string we're scanning.
    """
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].type is TokenType.IDENTIFIER
