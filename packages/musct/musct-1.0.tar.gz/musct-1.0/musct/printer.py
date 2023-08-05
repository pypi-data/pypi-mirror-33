import os
from sys import stdout
from typing import TextIO

no_confirm = False


class BufferedPrinter:
    _buffer: list
    _file: TextIO

    def __init__(self, file=stdout):
        self._buffer = []
        self._file = file

    def add(self, line: str):
        self._buffer.append(line)

    def clear(self):
        self._buffer = []

    def is_empty(self):
        return len(self._buffer) == 0

    def extend_buffer(self, lines: list):
        self._buffer.extend(lines)

    def print(self, clear=True):
        for line in self._buffer:
            print(line, file=self._file)
        if clear:
            self.clear()

    def print_line(self, line: str):
        print(line, file=self._file)


class InputPrinter(BufferedPrinter):
    def get_input(self, prompt: str) -> str:
        self.print()
        try:
            ipt = input(":: %s " % prompt)
        except EOFError:
            exit(os.EX_NOINPUT)
        return ipt


class ConfirmationPrinter(InputPrinter):
    _no_confirm: bool

    def __init__(self):
        super().__init__()
        self._no_confirm = no_confirm

    def get_input(self, prompt: str):
        input_str = super().get_input("%s [Y/n]" % prompt)
        confirm = [
            "Y",
            "y",
            "yes"
        ]
        if input_str in confirm or self._no_confirm:
            return True
        return False
