from typing import List

import pytest

from plox.expressions import Binary, Expr, Literal
from plox.parser import Parser
from plox.statements import Expression, Print
from plox.tokens import Token, TokenType

from tests.utilities import add_terminator


@pytest.mark.parametrize(
    "expr_tokens, expr",
    [
        ([Token(TokenType.NIL, "nil", None, 0)], Literal(None)),
        ([Token(TokenType.TRUE, "True", True, 0)], Literal(True)),
        ([Token(TokenType.STRING, "A string!", "A string!", 0)], Literal("A string!")),
        (
            [
                Token(TokenType.NUMBER, "1", 1.0, 0),
                Token(TokenType.PLUS, "+", None, 0),
                Token(TokenType.NUMBER, "2", 2.0, 0),
            ],
            Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0)),
        ),
    ],
)
def test_parsing_print_statements(expr_tokens: List[Token], expr: Expr):
    """Tests that we can parse a print statement containing a well formed
    expression.

    Arguments:
        expr_tokens: a stream of tokens that generates an expression.
        expr: an AST object that represents the parsed content of expr_tokens.
    """
    tokens = add_terminator(
        [
            Token(TokenType.PRINT, "print", None, 0),
            *expr_tokens,
            Token(TokenType.SEMICOLON, ";", None, 0),
        ]
    )
    statements = Parser(tokens).parse()
    assert len(statements) == 1
    assert statements[0] == Print(expr)


@pytest.mark.parametrize(
    "expr_tokens, expr",
    [
        ([Token(TokenType.NIL, "nil", None, 0)], Literal(None)),
        ([Token(TokenType.TRUE, "True", True, 0)], Literal(True)),
        ([Token(TokenType.STRING, "A string!", "A string!", 0)], Literal("A string!")),
        (
            [
                Token(TokenType.NUMBER, "1", 1.0, 0),
                Token(TokenType.PLUS, "+", None, 0),
                Token(TokenType.NUMBER, "2", 2.0, 0),
            ],
            Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0)),
        ),
    ],
)
def test_parsing_expression_statements(expr_tokens: List[Token], expr: Expr):
    """Tests that we can parse an expression statement containing a well formed
    expression.

    Arguments:
        expr_tokens: a stream of tokens that generates an expression.
        expr: an AST object that represents the parsed content of expr_tokens.
    """
    tokens = add_terminator(
        [
            *expr_tokens,
            Token(TokenType.SEMICOLON, ";", None, 0),
        ]
    )
    statements = Parser(tokens).parse()
    assert len(statements) == 1
    assert statements[0] == Expression(expr)
