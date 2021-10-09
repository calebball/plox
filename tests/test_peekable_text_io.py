from io import StringIO
from itertools import zip_longest

import pytest
from hypothesis import given, strategies as st

from plox.io import PeekableTextIO


MAXIMUM_INDEX = 2 ** 63 - 1


@given(string=st.text(), size=st.integers(min_value=1, max_value=MAXIMUM_INDEX))
def test_creating_peekable_text_io(string, size):
    PeekableTextIO(StringIO(string), size)


@given(string=st.text(), size=st.integers(max_value=0))
def test_negative_sizes_raise_value_error(string, size):
    with pytest.raises(ValueError) as excinfo:
        PeekableTextIO(StringIO(string), size)

    assert str(excinfo.value) == "Buffer size must be greater than 0"


@given(string=st.text(), size=st.integers(min_value=1, max_value=MAXIMUM_INDEX))
def test_buffer_is_filled_during_initialisation(string, size):
    stream = PeekableTextIO(StringIO(string), size)
    assert len(stream.buffer) == min(len(string), size)


@given(string=st.text(), size=st.integers(min_value=1, max_value=MAXIMUM_INDEX))
def test_advancing_through_the_string_returns_the_string(string, size):
    stream = PeekableTextIO(StringIO(string), size)
    for char in string:
        assert stream.advance() == char


@given(
    string=st.text(min_size=2), size=st.integers(min_value=2, max_value=MAXIMUM_INDEX)
)
def test_peek_shows_the_correct_character(string, size):
    stream = PeekableTextIO(StringIO(string), size)
    for char in string:
        assert stream.peek() == char
        stream.advance()


@given(
    string=st.text(min_size=2), size=st.integers(min_value=2, max_value=MAXIMUM_INDEX)
)
def test_successful_match_advances_the_stream(string, size):
    stream = PeekableTextIO(StringIO(string), size)
    for char, next_char in zip_longest(string, string[1:], fillvalue=""):
        assert stream.match(char)
        assert stream.peek() == next_char


@given(
    string=st.text(min_size=1), size=st.integers(min_value=2, max_value=MAXIMUM_INDEX)
)
def test_failed_match_advances_the_stream(string, size):
    stream = PeekableTextIO(StringIO(string), size)
    for char in string:
        assert not stream.match(None)
        assert stream.peek() == char
        stream.advance()


@given(string=st.text())
def test_advancing_reads_the_whole_input(string):
    stream = PeekableTextIO(StringIO(string), 1)
    chars = []
    while stream.peek():
        chars.append(stream.advance())

    assert "".join(chars) == string


@given(string=st.text())
def test_line_begins_at_one(string):
    stream = PeekableTextIO(StringIO(string), 1)
    assert stream.line == 1


@given(length=st.integers(min_value=1, max_value=100))
def test_string_of_newlines_is_ends_at_line_equal_to_length_plus_one(length):
    stream = PeekableTextIO(StringIO(length * "\n"), 1)
    while stream.advance():
        pass
    assert stream.line == length + 1


@pytest.mark.parametrize("string, line_lengths",
    [
        ("a\nb", [1]),
        ("abc\nde\nfg", [3, 2]),
    ]
)
def test_line_advances_correctly(string, line_lengths):
    stream = PeekableTextIO(StringIO(string), 1)
    for line_number, length in enumerate(line_lengths):
        for _ in range(length):
            stream.advance()
        assert stream.line == line_number + 1
