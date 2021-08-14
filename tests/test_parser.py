from typing import List

import pytest
from hypothesis import given, strategies as st

from plox.ast import Binary, Literal, Unary
from plox.parser import Parser
from plox.tokens import Token, TokenType


def add_terminator(tokens: List[Token]) -> List[Token]:
    return tokens + [Token(TokenType.EOF, "", None, 0)]


@pytest.mark.parametrize(
    "token",
    [
        Token(TokenType.FALSE, "false", False, 0),
        Token(TokenType.TRUE, "true", True, 0),
        Token(TokenType.NIL, "nil", None, 0),
        Token(TokenType.NUMBER, "number", 3.14159, 0),
        Token(TokenType.STRING, "string", "ohhai", 0),
    ],
)
def test_parsing_non_group_primary_expressions(token: Token):
    """Tests that we can parse a primary expression that is not a grouping.

    Arguments:
        token: the primary token that we're going to parse.
    """
    assert Parser(add_terminator([token])).parse() == Literal(token.literal)


@pytest.mark.parametrize(
    "tokens",
    [
        [
            Token(TokenType.BANG, "!", None, 0),
            Token(TokenType.FALSE, "false", False, 0),
        ],
        [Token(TokenType.BANG, "!", None, 0), Token(TokenType.TRUE, "true", True, 0)],
        [
            Token(TokenType.MINUS, "-", None, 0),
            Token(TokenType.NUMBER, "number", 3.14159, 0),
        ],
    ],
)
def test_parsing_basic_unary_expressions(tokens: List[Token]):
    """Tests that we can parse a unary expression with a non-grouping primary
    expression.

    Arguments:
        tokens: the token stream that should generate the expression. This
            stream does not include the terminating EOF token.
    """
    assert Parser(add_terminator(tokens)).parse() == Unary(
        tokens[0], Literal(tokens[1].literal)
    )


@pytest.mark.parametrize(
    "operator",
    [
        Token(TokenType.PLUS, "+", None, 0),
        Token(TokenType.MINUS, "-", None, 0),
        Token(TokenType.STAR, "*", None, 0),
        Token(TokenType.SLASH, "/", None, 0),
        Token(TokenType.LESS, "<", None, 0),
        Token(TokenType.LESS_EQUAL, "<=", None, 0),
        Token(TokenType.GREATER, ">", None, 0),
        Token(TokenType.GREATER_EQUAL, ">=", None, 0),
        Token(TokenType.EQUAL_EQUAL, "==", None, 0),
        Token(TokenType.BANG_EQUAL, "!=", None, 0),
    ],
)
def test_parsing_basic_binary_expressions(operator: Token):
    """Tests that we can parse a binary expression with non-grouping primary
    expressions.

    Arguments:
        operator: the binary operator that we'll place in a token sequence to
            generate a binary expression.
    """
    tokens = [
        Token(TokenType.NUMBER, "number", 3.14159, 0),
        operator,
        Token(TokenType.NUMBER, "number", 3.14159, 0),
    ]
    assert Parser(add_terminator(tokens)).parse() == Binary(
        Literal(tokens[0].literal), tokens[1], Literal(tokens[2].literal)
    )
