from typing import Any

from plox.tokens import Token


class LoxParseError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value
