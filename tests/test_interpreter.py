import pytest
from hypothesis import given, strategies as st

from plox.ast import Binary, Literal, Unary
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
    ]
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
        (Token(TokenType.PLUS, "+", None, 0), 3.),
        (Token(TokenType.MINUS, "-", None, 0), -1.),
        (Token(TokenType.STAR, "*", None, 0), 2.),
        (Token(TokenType.SLASH, "/", None, 0), 0.5),
    ]
)
def test_basic_arithmetic_expressions(operator: Token, expected: float):
    """Test that we correctly evaluate some very basic arithmetic operations.

    Arguments:
        operator: the arithmetic operator that we'll be evaluating.
        expected: the expected result of the expression.
    """
    expr = Binary(Literal(1), operator, Literal(2))
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
    ]
)
def test_basic_comparison_expressions(operator: Token, expected: float):
    """Test that we correctly evaluate some very basic numeric comparison
    operations.

    Arguments:
        operator: the comparison operator that we'll be evaluating.
        expected: the expected result of the expression.
    """
    expr = Binary(Literal(1), operator, Literal(2))
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
