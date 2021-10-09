from io import TextIOBase


class PeekableTextIO:
    def __init__(self, stream: TextIOBase, buffer: int):
        if buffer < 1:
            raise ValueError("Buffer size must be greater than 0")

        self.stream = stream
        self.buffer = tuple(stream.read(buffer))
        self.line = 1

    def advance(self) -> str:
        if not self.buffer:
            return ""

        char, *buffer = self.buffer
        if char == "\n":
            self.line += 1

        if (next_char := self.stream.read(1)):
            self.buffer = (*buffer, next_char)
        else:
            self.buffer = tuple(buffer)

        return char

    def peek(self, distance: int = 0) -> str:
        try:
            return self.buffer[distance]
        except IndexError:
            return ""

    def match(self, char: str) -> bool:
        if self.peek() == char:
            self.advance()
            return True
        return False
