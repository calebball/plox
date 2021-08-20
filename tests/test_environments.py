from typing import Any

import pytest
from hypothesis import given, strategies as st

from plox.environment import Environment
from plox.errors import LoxRuntimeError
from plox.tokens import Token, TokenType

from tests.utilities import identifiers, identifier_tokens, values


@given(
    name=identifier_tokens(),
    value=values(),
)
def test_declaring_and_retrieving_variables(name: Token, value: Any):
    """Tests that we can declare a variable and then immediately retrieve it.

    Arguments:
        name: an identifier token with the name that we'll declare and
            retrieve.
        value: the value that we'll initialise the variable with.
    """
    env = Environment()
    env.define(name.lexeme, value)
    assert env.get(name) == value


@given(
    name=identifier_tokens(),
)
def test_retrieving_undeclared_variable_raises_error(name: Token):
    """Tests that the environment raises a LoxRuntimeError if we try to
    retrieve an undeclared variable.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
    """
    env = Environment()
    with pytest.raises(LoxRuntimeError):
        env.get(name)


@given(
    name=identifier_tokens(),
    value=values(),
)
def test_declaring_and_assigning_variables(name: Token, value: Any):
    """Tests that we can declare a variable and then immediately assign a new
    value to it.

    Arguments:
        name: an identifier token with the name that we'll declare and
            retrieve.
        value: the value that we'll assign to the variable.
    """
    env = Environment()
    env.define(name.lexeme, None)
    env.assign(name, value)
    assert env.get(name) == value


@given(
    name=identifier_tokens(),
    value=values(),
)
def test_assigning_undeclared_variable_raises_error(name: Token, value: Any):
    """Tests that the environment raises a LoxRuntimeError if we try to
    assign an undeclared variable.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
        value: the value that we'll attempt to assign to the variable.
    """
    env = Environment()
    with pytest.raises(LoxRuntimeError):
        env.assign(name, value)


@given(
    name=identifier_tokens(),
    value=values(),
    depth=st.integers(min_value=1, max_value=10),
)
def test_retrieving_variable_from_outer_scope(name: Token, value: Any, depth: int):
    """Tests that we can retrieve a variable that has been declared in an outer
    scope.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
        value: the value that the variable will be initialised to.
        depth: the number of environments we'll create. The variable will be
            declared in the outermost environment and accessed from the
            innermost.
    """
    outer = Environment()
    inner = outer
    for _ in range(depth):
        inner = Environment(inner)
    outer.define(name.lexeme, value)
    assert inner.get(name) == value


@given(
    name=identifier_tokens(),
    value=values(),
    depth=st.integers(min_value=1, max_value=10),
)
def test_assigning_variable_from_outer_scope(name: Token, value: Any, depth: int):
    """Tests that we can assign to a variable that has been declared in an
    outer scope.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
        value: the value that we'll assign to the variable.
        depth: the number of environments we'll create. The variable will be
            declared in the outermost environment and accessed from the
            innermost.
    """
    outer = Environment()
    inner = outer
    for _ in range(depth):
        inner = Environment(inner)
    outer.define(name.lexeme, None)
    inner.assign(name, value)
    assert outer.get(name) == value


@given(
    name=identifier_tokens(),
    value=values(),
    depth=st.integers(min_value=1, max_value=10),
)
def test_inner_scopes_shadow_outer_scopes(name: Token, value: Any, depth: int):
    """Tests that if we define a variable in an inner scope that shares a name
    with an outer scope then the inner scope shadows the outer scope.

    This means that accessing the name from the inner scope does not return
    what's contained in the outer scope, and that the variable in the outer
    scope is not affected by the variable in the inner scope.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
        value: the value that the variable will be initialised to.
        depth: the number of environments we'll create. The variable will be
            declared in the outermost environment and accessed from the
            innermost.
    """
    outer = Environment()
    inner = outer
    for _ in range(depth):
        inner = Environment(inner)
    outer.define(name.lexeme, None)
    inner.define(name.lexeme, value)
    assert inner.get(name) == value
    assert outer.get(name) is None


@given(
    name=identifier_tokens(),
    value=values(),
    depth=st.integers(min_value=1, max_value=10),
)
def test_assigning_shadowed_variable_does_not_affect_outer_scope(
    name: Token, value: Any, depth: int
):
    """Tests that if we assign to a variable that is shadowing an outer scope
    then the outer scope is unaffected.

    Arguments:
        name: an identifier token with the name that we'll attempt to retrieve.
        value: the value that will be assigned to the inner variable.
        depth: the number of environments we'll create. The variable will be
            declared in the outermost environment and accessed from the
            innermost.
    """
    outer = Environment()
    inner = outer
    for _ in range(depth):
        inner = Environment(inner)
    outer.define(name.lexeme, None)
    inner.define(name.lexeme, None)
    inner.assign(name, value)
    assert inner.get(name) == value
    assert outer.get(name) is None
