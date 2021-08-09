import readline
import sys
from typing import List

from attr import define

from plox.scanner import Scanner


@define
class Plox:
    had_error: bool = False

    def main(self, args: List[str]):
        if len(args) > 1:
            print("Usage: plox [script]")
            sys.exit(64)

        if len(args) == 1:
            self.run_file(args[0])

        self.run_prompt()

    def run_file(self, path: str):
        with open(path, "r") as source:
            self.run(source.read())

        if self.had_error:
            sys.exit(65)

    def run_prompt(self):
        try:
            while True:
                line = input("> ")
                self.run(line)
                self.had_error = False
        except EOFError:
            pass

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        print(tokens)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True


def main():
    Plox().main(sys.argv[1:])
