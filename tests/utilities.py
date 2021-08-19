from typing import List

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
