from typing import List

from hypothesis import strategies as st

from plox.scanner import keywords
from plox.tokens import Token, TokenType


def add_terminator(tokens: List[Token]) -> List[Token]:
    """Add the final EOF token to a list of tokens to create a complete token
    stream.

    Arguments:
        tokens: the list of tokens to be terminated.

    Returns:
        A new list containing the contents of tokens followed by an EOF token.
    """
    return tokens + [Token(TokenType.EOF, "", None, 0)]


def identifiers():
    return (
        st.text(
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


def identifier_tokens(*args, **kwargs):
    return identifiers(*args, **kwargs).map(
        lambda name: Token(TokenType.IDENTIFIER, name, None, 0)
    )


def values():
    return st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    )
