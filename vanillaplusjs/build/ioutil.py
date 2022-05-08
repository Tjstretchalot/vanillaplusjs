"""Contains useful IO wrappers for tokenizers
"""


from typing import Optional
import re
from io import TextIOBase


CARRIAGE_RETURN_LIKE = re.compile(r"\r\n|\r|\f")
SURROGATE = re.compile(r"[\ud800-\udfff]")


class PeekableTextIO:
    """Wraps a text io in such a way that it can be peeked at."""

    def __init__(self, fp: TextIOBase):
        self.fp = fp
        self.buffer = ""
        self.seen_eof = False

    def read(self, n: int = -1) -> Optional[str]:
        """Reads and advances n characters. If n is -1, then reads all
        remaining characters.

        If we're at EOF, returns None.
        """
        if self.seen_eof:
            if not self.buffer:
                return None

            if n == -1 or len(self.buffer) <= n:
                res = self.buffer
                self.buffer = ""
                return res

            res = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return res

        if n == -1:
            self.seen_eof = True
            res = self.buffer + (self.fp.read() or "")
            self.buffer = ""
            return res

        if len(self.buffer) >= n:
            res = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return res

        new_data = self.fp.read(n - len(self.buffer))
        if new_data is None:
            self.seen_eof = True
            if not self.buffer:
                return None
            new_data = ""
        self.seen_eof = len(new_data) < n - len(self.buffer)
        res = self.buffer + new_data
        self.buffer = ""
        return res

    def peek(self, n: int = 1) -> Optional[str]:
        """Returns without advancing the next n characters. If n is -1, then
        returns all remaining characters.

        If we're at EOF, returns None.
        """
        if self.seen_eof:
            if not self.buffer:
                return None

            if n == -1 or len(self.buffer) <= n:
                return self.buffer

            return self.buffer[:n]

        if len(self.buffer) >= n:
            return self.buffer[:n]

        new_data = self.fp.read(n - len(self.buffer))
        if new_data is None:
            self.seen_eof = True
            if not self.buffer:
                return None
            new_data = ""
        self.seen_eof = len(new_data) < n - len(self.buffer)

        self.buffer += new_data
        return self.buffer


class PreprocessedTextIO:
    """Same interface as PeekableTextIO, except performs the necessary
    preprocessing described at https://www.w3.org/TR/css-syntax-3/#input-preprocessing
    """

    def __init__(self, fp: PeekableTextIO) -> None:
        self.fp = fp

    def _read(self, n: int = -1) -> Optional[str]:
        """Reads and advances n characters. If n is -1, then reads all
        remaining characters.

        If we're at EOF, returns None.

        This may return fewer characters than requested even if there
        are more characters available, due to substitutions.
        """
        res = self.fp.read(n)
        if res is None:
            return None
        if len(res) == n and res[-1] == "\r":
            if self.fp.peek(1) == "\n":
                res = res[:-1]

        res = CARRIAGE_RETURN_LIKE.sub("\n", res)
        res = SURROGATE.sub("\uFFFD", res)
        return res

    def _peek(self, n: int = 1) -> Optional[str]:
        """Returns without advancing the next n characters. If n is -1, then
        returns all remaining characters.

        If we're at EOF, returns None.

        This may return fewer characters than requested even if there
        are more characters available, due to substitutions.
        """
        res = self.fp.peek(n if n < 1 else n + 1)
        if res is None:
            return None
        if n >= 1 and len(res) == n + 1:
            if res[-2:] == "\r\n":
                res = res[:-2]
            else:
                res = res[:-1]

        res = CARRIAGE_RETURN_LIKE.sub("\n", res)
        res = SURROGATE.sub("\uFFFD", res)
        return res

    def read(self, n: int = -1) -> Optional[str]:
        """Reads and advances n characters. If n is -1, then reads all
        remaining characters.

        If we're at EOF, returns None.
        """
        res = self._read(n)
        if res is None or n < 1 or len(res) == n:
            return res

        if len(res) == 0:
            return None

        while len(res) < n:
            additional = self._read(n - len(res))
            if additional is None:
                return res
            res += additional

        return res

    def peek(self, n: int = 1) -> Optional[str]:
        """Returns without advancing the next n characters. If n is -1, then
        returns all remaining characters.

        If we're at EOF, returns None.
        """
        res = self._peek(n)
        if res is None or n < 1 or len(res) == n:
            return res

        if len(res) == 0:
            return None

        attempted_peek_length = n
        while True:
            old_actual_peek_length = len(res)
            missing_characters = n - old_actual_peek_length
            new_peek_length = attempted_peek_length + missing_characters
            res = self._peek(new_peek_length)
            if len(res) == n or len(res) == old_actual_peek_length:
                return res
            attempted_peek_length = new_peek_length
