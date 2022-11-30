"""Tokenizes a javascript document; converting a stream of characters into a stream
of tokens.

This only supports a subset of javascript tokens; in particular, we focus on only
just enough tokens that for a javascript module we can detect any import statements
that the document starts with.
"""
from io import TextIOBase
from typing import Generator, Optional
from .token import JSToken, JSTokenType
from vanillaplusjs.build.ioutil import PreprocessedTextIO, PeekableTextIO
import string
from .unicode_derived import is_id_start, is_id_continue


def tokenize(fp: TextIOBase) -> Generator[JSToken, None, None]:
    """Tokenizes the given file-like object, streaming back the
    tokens as they are parsed. This is not a compliant or complete tokenizer,
    and it does not synthesize semicolons.

    Args:
        fp (FileIO): a file-like object to parse

    Yields:
        JSToken: the next token

    Sends:
        None

    Returns:
        None
    """
    peekable = PreprocessedTextIO(PeekableTextIO(fp))
    del fp

    while peeked := peekable.peek(1):
        if (ws := _consume_whitespace(peekable)) is not None:
            yield ws
            continue

        if (comment := _consume_comment(peekable)) is not None:
            yield comment
            continue

        if (identifier := _consume_identifier(peekable)) is not None:
            yield identifier
            continue

        if _is_newline(peeked):
            peekable.read(1)
            yield JSToken(type=JSTokenType.line_terminator, value=None)
            continue

        if peeked == "{":
            peekable.read(1)
            yield JSToken(type=JSTokenType.open_curly_bracket, value=None)
            continue

        if peeked == "}":
            peekable.read(1)
            yield JSToken(type=JSTokenType.close_curly_bracket, value=None)
            continue

        if peeked == "*":
            peekable.read(1)
            yield JSToken(type=JSTokenType.asterisk, value=None)
            continue

        if peeked == ",":
            peekable.read(1)
            yield JSToken(type=JSTokenType.comma, value=None)
            continue

        if peeked == ";":
            peekable.read(1)
            yield JSToken(type=JSTokenType.semicolon, value=None)
            continue

        if peeked == '"':
            yield _consume_string_literal(peekable)
            continue

        if peeked == "'":
            yield _consume_string_literal(peekable)
            continue

        yield JSToken(type=JSTokenType.invalid, value=peekable.read(1))

    yield JSToken(type=JSTokenType.eof, value=None)


def tokenize_and_close(fp: TextIOBase) -> Generator[JSToken, None, None]:
    """The same as tokenize, except at the end it closes the file handle"""
    try:
        yield from tokenize(fp)
    finally:
        fp.close()


def _consume_whitespace(peekable: PeekableTextIO) -> Optional[JSToken]:
    """Consumes as much whitespace as possible from the given peekable
    https://tc39.es/ecma262/#sec-white-space
    """
    res = ""
    while (peeked := peekable.peek(1)) and _is_whitespace(peeked):
        res += peekable.read(1)

    if res:
        return JSToken(type=JSTokenType.whitespace, value=res)
    return None


def _consume_comment(peekable: PeekableTextIO) -> Optional[JSToken]:
    """Consumes a comment from the given peekable, if one is present."""
    next_2 = peekable.peek(2)
    if next_2 is None or len(next_2) != 2:
        return None

    if next_2 == "//":
        peekable.read(2)
        return _consume_single_line_comment(peekable)

    if next_2 == "/*":
        peekable.read(2)
        return _consume_multi_line_comment(peekable)

    return None


def _consume_single_line_comment(peekable: PeekableTextIO) -> Optional[JSToken]:
    """Consumes a single-line comment from the given peekable, if one is present.
    Assumes that the starting "//" has already been consumed.
    """
    res = ""
    while (peeked := peekable.peek(1)) and not _is_newline(peeked):
        res += peekable.read(1)
    return JSToken(type=JSTokenType.comment, value=res)


def _consume_multi_line_comment(peekable: PeekableTextIO) -> Optional[JSToken]:
    """Consumes a multi-line comment from the given peekable, if one is present.
    Assumes that the starting "/*" has already been consumed.
    """
    res = ""
    while (peeked := peekable.peek(2)) and peeked != "*/":
        res += peekable.read(1)

    if peeked == "*/":
        peekable.read(2)
    return JSToken(type=JSTokenType.comment, value=res)


RESERVED_IDENTIFIERS = {
    "as": JSTokenType.keyword_as,
    "from": JSTokenType.keyword_from,
    "import": JSTokenType.keyword_import,
}


def _consume_identifier(peekable: PeekableTextIO) -> Optional[JSToken]:
    """Consumes an identifier from the given peekable, if one is present."""
    res = ""
    while peeked := peekable.peek(1):
        if peeked == "\\" and _is_unicode_escape_sequence(peekable.peek(10)[1:]):
            peekable.read(1)
            res += _consume_unicode_escape_sequence(peekable)
        elif not res and is_id_start(peeked):
            res += peekable.read(1)
        elif res and (peeked in "$\u200C\u200D" or is_id_continue(peeked)):
            res += peekable.read(1)
        else:
            break

    if not res:
        return None

    if res in RESERVED_IDENTIFIERS:
        return JSToken(type=RESERVED_IDENTIFIERS[res], value=None)

    return JSToken(type=JSTokenType.identifier, value=res)


def _consume_unicode_escape_sequence(peekable: PeekableTextIO) -> Optional[str]:
    """Consumes a unicode escape sequence from the given peekable, if one is present.
    This consumes something like 'u1234' or 'u{1234}', and does not expect to start
    on a slash. Returns the actual unicode character; returns None if theres a parse
    error
    """
    if peekable.peek(1) != "u":
        return None
    peekable.read(1)

    res = ""
    if peekable.peek(1) == "{":
        peekable.read(1)
        while True:
            peeked = peekable.peek(1)
            if not peeked:
                return None
            if peeked == "}":
                break
            res += peekable.read(1)

        peekable.read(1)

        if any(c not in string.hexdigits for c in res):
            return None

        return chr(int(res, 16))

    while len(res) < 4:
        peeked = peekable.peek(1)
        if not peeked:
            return None

        if peeked not in string.hexdigits:
            return None
        res += peekable.read(1)

    return chr(int(res, 16))


def _consume_string_literal(peekable: PeekableTextIO) -> JSToken:
    """Consumes a string from the given peekable, assuming that the current
    peeked character is a quote.
    """
    quote = peekable.read(1)
    res = ""
    while True:
        peeked = peekable.peek(1)
        if not peeked or _is_newline(peeked):
            return JSToken(type=JSTokenType.invalid, value=quote + res)
        if peeked == quote:
            peekable.read(1)
            return JSToken(type=JSTokenType.string_literal, value=res)
        if peeked == "\\":
            if _is_unicode_escape_sequence(peekable.peek(10)[1:]):
                peekable.read(1)
                res += _consume_unicode_escape_sequence(peekable)
            else:
                peekable.read(1)
                peeked = peekable.peek(1)
                if not peeked:
                    return JSToken(type=JSTokenType.invalid, value=quote + res + "\\")

                escaped = peekable.read(1)
                if escaped == "n":
                    res += "\n"
                elif escaped == "r":
                    res += "\r"
                elif escaped == "t":
                    res += "\t"
                elif escaped == "b":
                    res += "\b"
                elif escaped == "f":
                    res += "\f"
                elif escaped == "v":
                    res += "\v"
                elif escaped == "0":
                    res += "\0"
                else:
                    res += escaped
        else:
            res += peekable.read(1)


WHITESPACE_CHARACTERS = frozenset(
    "\u0009\u000B\u000C\uFEFF\u0020\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000"
)


def _is_whitespace(char: str) -> bool:
    """Returns true if the given characters are all whitespace characters."""
    return char and all(ch in WHITESPACE_CHARACTERS for ch in char)


def _is_newline(char: str) -> bool:
    """Returns true if the given character is a newline character."""
    # Due to the noncompliant preprocessing we can ignore carriage returns
    return char in "\n\u2028\u2029"


def _is_unicode_escape_sequence(nine: str) -> bool:
    """Determines if the given nine characters could be consumed, perhaps partially,
    to get a valid unicode escape sequence.
    """
    if nine is None or len(nine) < 2:
        return False

    if nine[0] != "u":
        return False

    if nine[1] == "{":
        for i in range(2, len(nine) - 1):
            if nine[i] == "}":
                if i == 2:
                    return False
                hex_num = int(nine[2:i], 16)
                return hex_num <= 0x10FFFF
            if nine[i] not in string.hexdigits:
                return False

        return False

    return len(nine) >= 5 and all(c in string.hexdigits for c in nine[1:5])
