import readline
import sys
from io import StringIO, TextIOBase
from typing import List, Optional

from plox.errors import LoxRuntimeError
from plox.tokens import Token, TokenType


class Plox:
    HAD_ERROR: bool = False
    HAD_RUNTIME_ERROR: bool = False
    interpreter = None

    @classmethod
    def main(cls, args: List[str]):
        if len(args) > 1:
            print("Usage: plox [script]")
            sys.exit(64)

        if len(args) == 1:
            cls.run_file(args[0])

        else:
            cls.run_prompt()

    @classmethod
    def run_file(cls, path: str):
        with open(path, "r") as source:
            cls.run(source)

        if cls.HAD_ERROR:
            sys.exit(65)
        if cls.HAD_RUNTIME_ERROR:
            sys.exit(70)

    @classmethod
    def run_prompt(cls):
        try:
            while True:
                line = input("> ")
                cls.run(StringIO(line))
                cls.HAD_ERROR = False
        except EOFError:
            pass

    @classmethod
    def run(cls, source: TextIOBase):
        from plox.interpreter import Interpreter
        from plox.parser import Parser
        from plox.resolver import Resolver
        from plox.scanner import scan_tokens

        if cls.interpreter is None:
            cls.interpreter = Interpreter()

        tokens = scan_tokens(source)

        statements = Parser(tokens).parse()

        if cls.HAD_ERROR:
            return

        Resolver(cls.interpreter).resolve(statements)

        if cls.HAD_ERROR:
            return

        cls.interpreter.interpret(statements)

    @classmethod
    def error(cls, line: int, message: str, token: Optional[Token] = None):
        if token is None:
            where = ""
        elif token.type is TokenType.EOF:
            where = " at end"
        else:
            where = f" at '{token.lexeme}'"

        cls.report(line, where, message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        cls.HAD_ERROR = True

    @classmethod
    def runtime_error(cls, error: LoxRuntimeError):
        print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
        cls.HAD_RUNTIME_ERROR = True


def main():
    Plox.main(sys.argv[1:])
