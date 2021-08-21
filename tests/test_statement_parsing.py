from typing import List

import pytest
from hypothesis import given, strategies as st

from plox.expressions import Assign, Binary, Expr, Literal
from plox.parser import Parser
from plox.scanner import keywords
from plox.statements import Block, Expression, If, Print, Var
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


@given(
    identifier=st.text(
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
def test_parsing_non_initialised_variable_declarations(identifier: str):
    """Tests that we can parse a variable declaration that doesn't initialise
    the value of the variable.

    Uninitialised declaration is valid in Lox, and when evaluated it should
    result in a globally scoped identifier with a value of nil.

    Arguments:
        identifier: the variable name to declare.
    """
    tokens = add_terminator(
        [
            Token(TokenType.VAR, "var", None, 0),
            Token(TokenType.IDENTIFIER, identifier, None, 0),
            Token(TokenType.SEMICOLON, ";", None, 0),
        ]
    )
    statements = Parser(tokens).parse()
    assert len(statements) == 1
    assert statements[0] == Var(tokens[1], None)


@pytest.mark.parametrize(
    "initialiser",
    [
        [Token(TokenType.NIL, "nil", None, 0)],
        [Token(TokenType.TRUE, "True", True, 0)],
        [Token(TokenType.STRING, "ohhai", "ohhai", 0)],
        [Token(TokenType.NUMBER, "3.14159", 3.14159, 0)],
        [
            Token(TokenType.NUMBER, "1", 1.0, 0),
            Token(TokenType.PLUS, "+", None, 0),
            Token(TokenType.NUMBER, "2", 2.0, 0),
        ],
    ],
)
@given(
    identifier=st.text(
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
def test_parsing_initialised_variable_declarations(
    identifier: str, initialiser: List[Token]
):
    """Tests that we can parse a variable declaration that includes an
    initialising expression.

    Arguments:
        identifier: the variable name to declare.
        initialiser: the token stream that defines the initial value.
    """
    tokens = add_terminator(
        [
            Token(TokenType.VAR, "var", None, 0),
            Token(TokenType.IDENTIFIER, identifier, None, 0),
            Token(TokenType.EQUAL, "=", None, 0),
            *initialiser,
            Token(TokenType.SEMICOLON, ";", None, 0),
        ]
    )
    statements = Parser(tokens).parse()
    expr_tokens = add_terminator(initialiser)
    expr = Parser(expr_tokens).expression()
    assert len(statements) == 1
    assert statements[0] == Var(tokens[1], expr)


@pytest.mark.parametrize(
    "tokens, expr",
    [
        (
            [
                Token(TokenType.NUMBER, "1", 1.0, 0),
                Token(TokenType.SEMICOLON, ";", None, 0),
            ],
            Expression(Literal(1.0)),
        ),
        (
            [
                Token(TokenType.NUMBER, "1", 1.0, 0),
                Token(TokenType.PLUS, "+", None, 0),
                Token(TokenType.NUMBER, "2", 2.0, 0),
                Token(TokenType.SEMICOLON, ";", None, 0),
            ],
            Expression(
                Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0))
            ),
        ),
    ],
)
def test_parsing_block_statements_with_a_single_expression(
    tokens: List[Token], expr: Expr
):
    """Tests that if we can parse an expression statement wrapped in a block
    correctly.

    Arguments:
        tokens: the list of tokens that creates the expression.
        expr: the expected expression.
    """
    tokens = add_terminator(
        [
            Token(TokenType.LEFT_BRACE, "{", None, 0),
            *tokens,
            Token(TokenType.RIGHT_BRACE, "}", None, 0),
        ]
    )
    assert Parser(tokens).parse() == [Block([expr])]


@pytest.mark.parametrize(
    "tokens, condition, then_branch",
    [
        (
            [
                Token(TokenType.IF, "if", None, 0),
                Token(TokenType.LEFT_PAREN, "(", None, 0),
                Token(TokenType.TRUE, "true", None, 0),
                Token(TokenType.RIGHT_PAREN, ")", None, 0),
                Token(TokenType.NIL, "nil", None, 0),
                Token(TokenType.SEMICOLON, ";", None, 0),
            ],
            Literal(True),
            Expression(Literal(None)),
        ),
    ],
)
def test_parsing_if_statements_with_no_else_clause(
    tokens: List[Token], condition: Expr, then_branch: Expr
):
    """Tests that we can parse an if statement with no else clause.

    Arguments:
        tokens: the token stream that generates the if statement.
        condition: the expression expected as the if conditional.
        then_branch: the expression expected in the body of the if statement.
    """
    tokens = add_terminator(tokens)
    assert Parser(tokens).parse() == [If(condition, then_branch, None)]


@pytest.mark.parametrize(
    "tokens, condition, then_branch, else_branch",
    [
        (
            [
                Token(TokenType.IF, "if", None, 0),
                Token(TokenType.LEFT_PAREN, "(", None, 0),
                Token(TokenType.TRUE, "true", None, 0),
                Token(TokenType.RIGHT_PAREN, ")", None, 0),
                Token(TokenType.IDENTIFIER, "foo", None, 0),
                Token(TokenType.EQUAL, "=", None, 0),
                Token(TokenType.STRING, '"bar"', "bar", 0),
                Token(TokenType.SEMICOLON, ";", None, 0),
                Token(TokenType.ELSE, "else", None, 0),
                Token(TokenType.IDENTIFIER, "foo", None, 0),
                Token(TokenType.EQUAL, "=", None, 0),
                Token(TokenType.STRING, '"baz"', "baz", 0),
                Token(TokenType.SEMICOLON, ";", None, 0),
            ],
            Literal(True),
            Expression(
                Assign(Token(TokenType.IDENTIFIER, "foo", None, 0), Literal("bar"))
            ),
            Expression(
                Assign(Token(TokenType.IDENTIFIER, "foo", None, 0), Literal("baz"))
            ),
        ),
    ],
)
def test_parsing_if_statements_with_else_clause(
    tokens: List[Token], condition: Expr, then_branch: Expr, else_branch: Expr
):
    """Tests that we can parse an if statement with an else clause.

    Arguments:
        tokens: the token stream that generates the if statement.
        condition: the expression expected as the if conditional.
        then_branch: the expression expected as the then statement.
        else_branch: the expression expected as the else statement.
    """
    tokens = add_terminator(tokens)
    assert Parser(tokens).parse() == [If(condition, then_branch, else_branch)]


def test_parsing_nested_if_statements_with_else_clause():
    """Tests that we parse two if tokens follwed by a single else token in the
    correct way.

    This is defined outside of the grammar as the else token binding to the
    nearest if token.
    """
    tokens = add_terminator(
        [
            Token(TokenType.IF, "if", None, 0),
            Token(TokenType.LEFT_PAREN, "(", None, 0),
            Token(TokenType.TRUE, "true", None, 0),
            Token(TokenType.RIGHT_PAREN, ")", None, 0),
            Token(TokenType.IF, "if", None, 0),
            Token(TokenType.LEFT_PAREN, "(", None, 0),
            Token(TokenType.TRUE, "true", None, 0),
            Token(TokenType.RIGHT_PAREN, ")", None, 0),
            Token(TokenType.NUMBER, "1", 1.0, 0),
            Token(TokenType.SEMICOLON, ";", None, 0),
            Token(TokenType.ELSE, "else", None, 0),
            Token(TokenType.NUMBER, "1", 1.0, 0),
            Token(TokenType.SEMICOLON, ";", None, 0),
        ]
    )
    assert Parser(tokens).parse() == [
        If(
            Literal(True),
            If(Literal(True), Expression(Literal(1.0)), Expression(Literal(1.0))),
            None,
        )
    ]
