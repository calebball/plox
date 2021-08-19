import itertools
from typing import Any

import pytest
from hypothesis import assume, given, strategies as st

from plox.environment import Environment
from plox.expressions import Binary, Literal, Unary, Variable
from plox.errors import LoxRuntimeError
from plox.interpreter import Interpreter
from plox.tokens import Token, TokenType


@given(
    expr=st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal)
)
def test_interpreting_literal_expression(expr: Literal):
    """Test that we correctly interpret literal expressions.

    This is, of course, very straightforward because we're just returning a
    value. Numbers pose a bit of a problem though because of NaN, so we're
    rejecting both NaN and infinity from the test set. This will probably
    cause problems later on, but we'll need separate tests anyway.

    Arguments:
        expr: the literal expression that we will interpret.
    """
    assert expr.accept(Interpreter()) == expr.value


@given(number=st.floats(allow_nan=False, allow_infinity=False))
def test_interpreting_unary_negation_expression(number: float):
    """Test that we correctly interpret a unary expression that reverses the
    sign of a number literal.

    Arguments:
        number: the number that we're negating.
    """
    expr = Unary(Token(TokenType.MINUS, "-", None, 0), Literal(number))
    assert expr.accept(Interpreter()) == -number


@given(
    literal=st.one_of(
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal)
)
def test_interpreting_not_number_or_string_expression(literal: Literal):
    """Test that we correctly interpret a unary expression for the logical
    negation of a number or string literal.

    Lox's truthiness rules take all numbers and strings as truthy.

    Arguments:
        literal: the literal expression that we're logically negating.
    """
    expr = Unary(Token(TokenType.BANG, "-", None, 0), literal)
    assert expr.accept(Interpreter()) is False


@pytest.mark.parametrize(
    "literal, expected",
    [
        (Literal(None), True),
        (Literal(True), False),
        (Literal(False), True),
    ],
)
def test_interpreting_not_nil_or_bool_expression(literal: Literal, expected: bool):
    """Test that we correctly interpret a unary expression for the logical
    negation of a nil or boolean literal.

    Lox's truthiness rules take `nil` as falsy and treats booleans as expected.

    Arguments:
        literal: the literal expression that we're logically negating.
        expected: the expected result of evaluating the unary expression.
    """
    expr = Unary(Token(TokenType.BANG, "-", None, 0), literal)
    assert expr.accept(Interpreter()) is expected


@pytest.mark.parametrize(
    "operator, expected",
    [
        (Token(TokenType.PLUS, "+", None, 0), 3.0),
        (Token(TokenType.MINUS, "-", None, 0), -1.0),
        (Token(TokenType.STAR, "*", None, 0), 2.0),
        (Token(TokenType.SLASH, "/", None, 0), 0.5),
    ],
)
def test_basic_arithmetic_expressions(operator: Token, expected: float):
    """Test that we correctly evaluate some very basic arithmetic operations.

    Arguments:
        operator: the arithmetic operator that we'll be evaluating.
        expected: the expected result of the expression.
    """
    expr = Binary(Literal(1.0), operator, Literal(2.0))
    assert expr.accept(Interpreter()) == expected


@given(
    left=st.text(),
    right=st.text(),
)
def test_concatenating_string_with_plus_operator(left: str, right: str):
    """Test that we correctly concatenate two strings when we apply the plus
    operator to them.

    Arguments:
        left: the first string to appear in the expression.
        right: the second string to appear in the expression.
    """
    expr = Binary(Literal(left), Token(TokenType.PLUS, "+", None, 0), Literal(right))
    assert expr.accept(Interpreter()) == "".join([left, right])


@pytest.mark.parametrize(
    "operator, expected",
    [
        (Token(TokenType.GREATER, ">", None, 0), False),
        (Token(TokenType.GREATER_EQUAL, ">=", None, 0), False),
        (Token(TokenType.LESS, "<", None, 0), True),
        (Token(TokenType.LESS_EQUAL, "<=", None, 0), True),
    ],
)
def test_basic_comparison_expressions(operator: Token, expected: float):
    """Test that we correctly evaluate some very basic numeric comparison
    operations.

    Arguments:
        operator: the comparison operator that we'll be evaluating.
        expected: the expected result of the expression.
    """
    expr = Binary(Literal(1.0), operator, Literal(2.0))
    assert expr.accept(Interpreter()) is expected


@given(
    left=st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal),
    right=st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal),
)
def test_basic_equality_expressions(left: Literal, right: Literal):
    """Test that we correctly evaluate equality comparisons of literal
    expressions.

    Lox's equality logic matches python's, so this test is quite easy to
    express.

    Arguments:
        left: the first literal to appear in the expression.
        right: the second literal to appear in the expression.
    """
    expr = Binary(left, Token(TokenType.EQUAL_EQUAL, "==", None, 0), right)
    assert expr.accept(Interpreter()) is (left.value == right.value)


@given(
    left=st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal),
    right=st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ).map(Literal),
)
def test_basic_not_equality_expressions(left: Literal, right: Literal):
    """Test that we correctly evaluate not equal comparisons of literal
    expressions.

    Lox's equality logic matches python's, so this test is quite easy to
    express.

    Arguments:
        left: the first literal to appear in the expression.
        right: the second literal to appear in the expression.
    """
    expr = Binary(left, Token(TokenType.BANG_EQUAL, "!=", None, 0), right)
    assert expr.accept(Interpreter()) is (left.value != right.value)


@given(
    literal=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
    ).map(Literal),
)
def test_negating_non_number_raises_exception(literal: Literal):
    """Tests that if we attempt to evaluate the negation of a non-numeric
    literal then a LoxRuntimeError is raised to halt evaluation.

    Arguments:
        literal: the literal expression we'll attempt to negate.
    """
    expr = Unary(Token(TokenType.MINUS, "-", None, 0), literal)
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


@pytest.mark.parametrize(
    "operator",
    [
        Token(TokenType.GREATER, ">", None, 0),
        Token(TokenType.GREATER_EQUAL, ">=", None, 0),
        Token(TokenType.LESS, "<", None, 0),
        Token(TokenType.LESS_EQUAL, "<=", None, 0),
    ],
)
@given(
    left=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
    right=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
)
def test_comparison_of_non_numbers_raises_exception(
    operator: Token, left: Literal, right: Literal
):
    """Tests that if we attempt to compare two literals where at least one is
    not a number then a LoxRuntimeError is raised.

    Arguments:
        operator: the comparison operator used in the expression.
        left: the literal that appears first in the expression.
        right: the literal that appears second in the expression.
    """
    assume(not (isinstance(left.value, float) and isinstance(right.value, float)))
    print(left.value, right.value)
    expr = Binary(left, operator, right)
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


@pytest.mark.parametrize(
    "operator",
    [
        Token(TokenType.MINUS, "-", None, 0),
        Token(TokenType.STAR, "*", None, 0),
        Token(TokenType.SLASH, "/", None, 0),
    ],
)
@given(
    left=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
    right=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
)
def test_arithmetic_of_non_numbers_raises_exception(
    operator: Token, left: Literal, right: Literal
):
    """Tests that if we attempt to perform some arithmetic of two literals
    where at least one is not a number then a LoxRuntimeError is raised.

    Arguments:
        operator: the comparison operator used in the expression.
        left: the literal that appears first in the expression.
        right: the literal that appears second in the expression.
    """
    assume(not (isinstance(left.value, float) and isinstance(right.value, float)))
    expr = Binary(left, operator, right)
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


@given(
    left=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
    right=st.one_of(
        st.none(),
        st.booleans(),
        st.text(),
        st.floats(allow_nan=False, allow_infinity=False),
    ).map(Literal),
)
def test_summation_of_non_matching_types_raises_exception(
    left: Literal, right: Literal
):
    """Tests that if we attempt to add two literals where the types do not
    match then a LoxRuntimeError.

    Arguments:
        left: the literal that appears first in the expression.
        right: the literal that appears second in the expression.
    """
    assume(type(left.value) != type(right.value))
    expr = Binary(left, Token(TokenType.PLUS, "+", None, 0), right)
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


def test_summation_of_nil_raises_exception():
    """Tests that if we attempt to add two nil literals then a LoxRuntimeError
    is raised.
    """
    expr = Binary(Literal(None), Token(TokenType.PLUS, "+", None, 0), Literal(None))
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


@pytest.mark.parametrize(
    "left, right",
    [
        (Literal(left), Literal(right))
        for left, right in itertools.product([True, False], [True, False])
    ],
)
def test_summation_of_booleans_raises_exception(left: Literal, right: Literal):
    """Tests that if we attempt to add two boolean literals then a
    LoxRuntimeError is raised.

    Arguments:
        left: the literal that appears first in the expression.
        right: the literal that appears second in the expression.
    """
    expr = Binary(left, Token(TokenType.PLUS, "+", None, 0), right)
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())


@pytest.mark.parametrize("name, value", [("foo", "bar"), ("baz", 4.0)])
def test_evaluating_variable_reference(name: str, value: Any):
    """Tests that if the interpreter encounters an initialised reference then
    it correctly retrieves it from the environment.

    Arguments:
        name: the name of the variable that is being accessed.
        value: the value that the variable is initialised with.
    """
    env = Environment()
    env.define(name, value)
    expr = Variable(Token(TokenType.IDENTIFIER, name, None, 0))
    assert expr.accept(Interpreter(env)) == value


@pytest.mark.parametrize("name", ["foo", "bar", "b4z"])
def test_evaluating_uninitialised_variable_raise_error(name: str):
    """Tests that if the interpreter encounters an uninitialised reference then
    a LoxRuntimeError is raised.

    Arguments:
        name: the name of the variable that we attempt to access.
    """
    expr = Variable(Token(TokenType.IDENTIFIER, name, None, 0))
    with pytest.raises(LoxRuntimeError):
        expr.accept(Interpreter())
