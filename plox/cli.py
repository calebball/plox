import readline
import sys
from typing import List


class Plox:
    HAD_ERROR: bool = False

    @classmethod
    def main(cls, args: List[str]):
        if len(args) > 1:
            print("Usage: plox [script]")
            sys.exit(64)

        if len(args) == 1:
            cls.run_file(args[0])

        cls.run_prompt()

    @classmethod
    def run_file(cls, path: str):
        with open(path, "r") as source:
            cls.run(source.read())

        if cls.HAD_ERROR:
            sys.exit(65)

    @classmethod
    def run_prompt(cls):
        try:
            while True:
                line = input("> ")
                cls.run(line)
                cls.HAD_ERROR = False
        except EOFError:
            pass

    @classmethod
    def run(cls, source: str):
        from plox.scanner import Scanner

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        print(tokens)

    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        cls.HAD_ERROR = True


def main():
    Plox.main(sys.argv[1:])
