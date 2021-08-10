import glob
import os.path
from typing import List

import pytest

from plox.scanner import Scanner
from plox.tokens import Token


examples_directory = os.path.join(os.path.dirname(__file__), "examples")


def example_source(example: str) -> str:
    filename = os.path.join(examples_directory, f"{example}.lox")
    with open(filename, "r") as file:
        return file.read()


def example_tokens(example: str) -> List[Token]:
    filename = os.path.join(examples_directory, f"{example}.tokens")
    with open(filename, "r") as file:
        return [Token.from_str(line) for line in file.readlines()]


@pytest.mark.parametrize(
    "example",
    [
        os.path.splitext(os.path.basename(token_filename))[0]
        for token_filename in glob.glob(os.path.join(examples_directory, "*.tokens"))
    ],
)
def test_scanning_example(example: str):
    """Test that the scanner output for an example Lox source file matches the
    list of serialised tokens present in an example token file.

    Arguments:
        example: the name of the example to scan.
    """
    assert Scanner(example_source(example)).scan_tokens() == example_tokens(example)
