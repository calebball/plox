import itertools
from typing import List

import pytest
from hypothesis import given, strategies as st

from plox.expressions import Binary, Literal, Unary
from plox.parser import Parser
from plox.tokens import Token, TokenType


def add_terminator(tokens: List[Token]) -> List[Token]:
    return tokens + [Token(TokenType.EOF, "", None, 0)]


equality_operators = [
    Token(TokenType.EQUAL_EQUAL, "==", None, 0),
    Token(TokenType.BANG_EQUAL, "!=", None, 0),
]

comparison_operators = [
    Token(TokenType.LESS, "<", None, 0),
    Token(TokenType.LESS_EQUAL, "<=", None, 0),
    Token(TokenType.GREATER, ">", None, 0),
    Token(TokenType.GREATER_EQUAL, ">=", None, 0),
]

term_operators = [
    Token(TokenType.PLUS, "+", None, 0),
    Token(TokenType.MINUS, "-", None, 0),
]

factor_operators = [
    Token(TokenType.STAR, "*", None, 0),
    Token(TokenType.SLASH, "/", None, 0),
]

unary_operators = [
    Token(TokenType.MINUS, "-", None, 0),
    Token(TokenType.BANG, "!", None, 0),
]


@pytest.mark.parametrize(
    "token",
    [
        Token(TokenType.FALSE, "false", False, 0),
        Token(TokenType.TRUE, "true", True, 0),
        Token(TokenType.NIL, "nil", None, 0),
        Token(TokenType.NUMBER, "3.14159", 3.14159, 0),
        Token(TokenType.STRING, "ohhai", "ohhai", 0),
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
            Token(TokenType.NUMBER, "3.14159", 3.14159, 0),
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
    itertools.chain(
        equality_operators, comparison_operators, term_operators, factor_operators
    ),
)
def test_parsing_basic_binary_expressions(operator: Token):
    """Tests that we can parse a binary expression with non-grouping primary
    expressions.

    Arguments:
        operator: the binary operator that we'll place in a token sequence to
            generate a binary expression.
    """
    tokens = add_terminator(
        [
            Token(TokenType.NUMBER, "3.14159", 3.14159, 0),
            operator,
            Token(TokenType.NUMBER, "3.14159", 3.14159, 0),
        ]
    )
    assert Parser(tokens).parse() == Binary(
        Literal(tokens[0].literal), tokens[1], Literal(tokens[2].literal)
    )


@pytest.mark.parametrize(
    "left_operator, right_operator",
    itertools.chain.from_iterable(
        itertools.product(token_set, token_set)
        for token_set in [
            equality_operators,
            comparison_operators,
            term_operators,
            factor_operators,
        ]
    ),
)
def test_binary_expressions_are_left_associativity(
    left_operator: Token, right_operator: Token
):
    """Tests that all binary expressions are left associative.

    This is a very basic test with just two binary operators.

    Arguments:
        left_operator: the operator that appears first in the token stream.
        right_operator: the operator that appears second in the token stream.
    """
    tokens = add_terminator(
        [
            Token(TokenType.NUMBER, "1", 1, 0),
            left_operator,
            Token(TokenType.NUMBER, "2", 2, 0),
            right_operator,
            Token(TokenType.NUMBER, "3", 3, 0),
        ]
    )
    assert Parser(tokens).parse() == Binary(
        Binary(Literal(1), left_operator, Literal(2)), right_operator, Literal(3)
    )


@pytest.mark.parametrize(
    "left_operator, right_operator", itertools.product(unary_operators, unary_operators)
)
def test_unary_expressions_are_right_associative(
    left_operator: Token, right_operator: Token
):
    """Tests that unary expressions are right associative.

    This is a simple test with just two binary operators. The primary
    expressions used are just numbers, which probably makes the token streams
    a little odd when the ! operator is included.

    Arguments:
        left_operator: the operator that appears first in the token stream.
        right_operator: the operator that appears second in the token stream.
    """
    tokens = add_terminator(
        [
            left_operator,
            right_operator,
            Token(TokenType.NUMBER, "1", 1, 0),
        ]
    )
    assert Parser(tokens).parse() == Unary(
        left_operator, Unary(right_operator, Literal(1))
    )


@pytest.mark.parametrize(
    "left_operator, right_operator",
    itertools.chain(
        itertools.product(factor_operators, term_operators),
        itertools.product(factor_operators, comparison_operators),
        itertools.product(factor_operators, equality_operators),
        itertools.product(term_operators, comparison_operators),
        itertools.product(term_operators, equality_operators),
        itertools.product(comparison_operators, equality_operators),
    ),
)
def test_higher_then_lower_precedence_binary_expressions(
    left_operator: Token, right_operator: Token
):
    """Tests that binary operators are parsed with the correct precedence.

    Arguments:
        left_operator: the operator that appears first in the token stream.
        right_operator: the operator that appears second in the token stream.
    """
    tokens = add_terminator(
        [
            Token(TokenType.NUMBER, "1", 1, 0),
            left_operator,
            Token(TokenType.NUMBER, "2", 2, 0),
            right_operator,
            Token(TokenType.NUMBER, "3", 3, 0),
        ]
    )
    assert Parser(tokens).parse() == Binary(
        Binary(Literal(1), left_operator, Literal(2)), right_operator, Literal(3)
    )


@pytest.mark.parametrize(
    "left_operator, right_operator",
    itertools.chain(
        itertools.product(term_operators, factor_operators),
        itertools.product(comparison_operators, factor_operators),
        itertools.product(equality_operators, factor_operators),
        itertools.product(comparison_operators, term_operators),
        itertools.product(equality_operators, term_operators),
        itertools.product(equality_operators, comparison_operators),
    ),
)
def test_lower_then_higher_precedence_binary_expressions(
    left_operator: Token, right_operator: Token
):
    """Tests that binary operators are parsed with the correct precedence.

    Arguments:
        left_operator: the operator that appears first in the token stream.
        right_operator: the operator that appears second in the token stream.
    """
    tokens = add_terminator(
        [
            Token(TokenType.NUMBER, "1", 1, 0),
            left_operator,
            Token(TokenType.NUMBER, "2", 2, 0),
            right_operator,
            Token(TokenType.NUMBER, "3", 3, 0),
        ]
    )
    assert Parser(tokens).parse() == Binary(
        Literal(1), left_operator, Binary(Literal(2), right_operator, Literal(3))
    )


@pytest.mark.parametrize(
    "binary_operator, left_unary, right_unary",
    itertools.product(
        itertools.chain(
            equality_operators, comparison_operators, term_operators, factor_operators
        ),
        unary_operators,
        unary_operators,
    ),
)
def test_unary_expressions_are_higher_precedence_than_binary(
    binary_operator: Token, left_unary: Token, right_unary: Token
):
    """Test that unary expressions are correctly parsed as being higher
    precedence than any binary operator.

    Arguments:
        binary_operator: the binary operator that will appear between the two
            unary expressions.
        left_unary: the unary operator that will be applied to the first
            primary token.
        right_unary: the unary operator that will be applied to the second
            primary token.
    """
    tokens = add_terminator(
        [
            left_unary,
            Token(TokenType.NUMBER, "1", 1, 0),
            binary_operator,
            right_unary,
            Token(TokenType.NUMBER, "2", 2, 0),
        ]
    )
    assert Parser(tokens).parse() == Binary(
        Unary(left_unary, Literal(1)),
        binary_operator,
        Unary(right_unary, Literal(2)),
    )
