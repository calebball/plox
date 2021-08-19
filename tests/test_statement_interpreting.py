import pytest

from plox.expressions import Binary, Expr, Literal
from plox.interpreter import Interpreter
from plox.statements import Expression, Print
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
