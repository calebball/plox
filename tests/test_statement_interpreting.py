from typing import Any

import pytest

from plox.environment import Environment
from plox.expressions import Assign, Binary, Expr, Literal
from plox.interpreter import Interpreter
from plox.statements import Expression, If, Print, Var
from plox.tokens import Token, TokenType


@pytest.mark.parametrize(
    "expr",
    [
        Literal(None),
        Literal(True),
        Literal("A string!"),
        Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0)),
    ],
)
def test_interpreting_expression_statement(expr: Expr):
    """Tests that evaluating a valid expression statement does not raise any
    exceptions.

    Because statements do not return a value I think this might be all we can
    achieve, at least until a bit more machinery is in place and we can observe
    side effects in the interpreter.

    Arguments:
        expr: the expression that the statement will contain.
    """
    stmt = Expression(expr)
    stmt.accept(Interpreter())


@pytest.mark.parametrize(
    "expr, expected",
    [
        (Literal(None), "nil\n"),
        (Literal(True), "True\n"),
        (Literal("A string!"), "A string!\n"),
        (
            Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0)),
            "3\n",
        ),
    ],
)
def test_interpreting_print_statement(capsys, expr: Expr, expected: str):
    """Tests that evaluating a valid print statement writes the correct string
    to stdout.

    Arguments:
        expr: the expression that the statement will contain.
        expected: the string expected to be written to stdout.
    """
    stmt = Print(expr)
    stmt.accept(Interpreter())
    captured = capsys.readouterr()
    assert captured.out == expected


@pytest.mark.parametrize(
    "identifier",
    [
        Token(TokenType.IDENTIFIER, "foo", None, 0),
        Token(TokenType.IDENTIFIER, "b4r", None, 0),
    ],
)
def test_interpreting_uninitialised_variable_declarations(identifier: Token):
    """Tests that evaluating a variable declaration with no initialiser results
    in a name being added to the environment with a value of nil.

    Arguments:
        identifier: the identifier token in the variable declaration.
    """
    stmt = Var(identifier, None)
    env = Environment()
    stmt.accept(Interpreter(env))
    assert env.get(identifier) is None


@pytest.mark.parametrize(
    "identifier, value, expected",
    [
        (Token(TokenType.IDENTIFIER, "foo", None, 0), Literal("bar"), "bar"),
        (
            Token(TokenType.IDENTIFIER, "b4r", None, 0),
            Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 0), Literal(2.0)),
            3.0,
        ),
        (Token(TokenType.IDENTIFIER, "null", None, 0), Literal(None), None),
    ],
)
def test_interpreting_initialised_variable_declarations(
    identifier: Token, value: Expr, expected: Any
):
    """Tests that evaluating a variable declaration with an initialiser results
    in a name being added to the environment with the expected result of the
    initialising expression.

    Arguments:
        identifier: the identifier token in the variable declaration.
        value: the initialising expression.
        expected: the expected value of the initialised variable.
    """
    stmt = Var(identifier, value)
    env = Environment()
    stmt.accept(Interpreter(env))
    assert env.get(identifier) == expected


@pytest.mark.parametrize(
    "stmt, value",
    [
        (
            If(
                Literal(True),
                Expression(
                    Assign(Token(TokenType.IDENTIFIER, "foo", None, 0), Literal("bar"))
                ),
                Expression(
                    Assign(Token(TokenType.IDENTIFIER, "foo", None, 0), Literal("baz"))
                ),
            ),
            "bar",
        ),
    ],
)
def test_evaluating_if_statements_with_else_clause(stmt: If, value: Any):
    """Tests that we evaluate an if statement correctly by observing the value
    assigned to the variable `foo`.

    Arguments:
        stmt: the if statement that we'll evaluate.
        value: the expected value of `foo` after that statement is evaluated.
    """
    env = Environment()
    env.define("foo", None)
    stmt.accept(Interpreter(env))
    assert env.get(Token(TokenType.IDENTIFIER, "foo", None, 0)) == value
