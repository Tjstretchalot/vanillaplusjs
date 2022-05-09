"""Module for tokenizing a PREPROCESSOR icon comment. A full tokenizer
might seem overboard but we already have 2 tokenizers in the project,
what's one more?

Plus it's pretty convenient to have comment support, and it allows the
arguments to be more sophisticated
"""
from io import TextIOBase
from typing import Generator, Optional

from vanillaplusjs.build.css.token import CSSTokenType
from .token import IconToken, IconTokenType
from vanillaplusjs.build.ioutil import PreprocessedTextIO, PeekableTextIO
from vanillaplusjs.build.css.tokenizer import (
    _is_whitespace,
    _is_ident_start_codepoint,
    _is_ident_sequence,
    _consume_ident_sequence,
    _consume_string as _consume_css_string,
    _consume_number as _consume_css_number,
    _is_number,
)


def tokenize(fp: TextIOBase) -> Generator[IconToken, None, None]:
    """Tokenizes the given file-like object, streaming back the
    tokens as they are parsed.

    Args:
        fp (FileIO): a file-like object to parse

    Yields:
        IconToken: the next token

    Sends:
        None

    Returns:
        None
    """
    peekable = PreprocessedTextIO(PeekableTextIO(fp))
    del fp

    while peeked := peekable.peek(1):
        if (comment := _consume_comment(peekable)) is not None:
            yield comment
            continue

        if (ws := _consume_whitespace(peekable)) is not None:
            yield ws
            continue

        if _is_ident_start_codepoint(peeked):
            yield _consume_ident_like(peekable)
            continue

        if peeked in ("'", '"'):
            yield _consume_string(peekable)
            continue

        if peeked == ":":
            yield IconToken(type=IconTokenType.colon, value=None)
            peekable.read(1)
            continue

        if peeked == ",":
            yield IconToken(type=IconTokenType.comma, value=None)
            peekable.read(1)
            continue

        if peeked == "{":
            yield IconToken(type=IconTokenType.open_curly_bracket, value=None)
            peekable.read(1)
            continue

        if peeked == "}":
            yield IconToken(type=IconTokenType.close_curly_bracket, value=None)
            peekable.read(1)
            continue

        if peeked == "[":
            yield IconToken(type=IconTokenType.open_square_bracket, value=None)
            peekable.read(1)
            continue

        if peeked == "]":
            yield IconToken(type=IconTokenType.close_square_bracket, value=None)
            peekable.read(1)
            continue

        if peeked == ".":
            if _is_number(peekable.peek(3)):
                yield _consume_number(peekable)
                continue

            peekable.read(1)
            yield IconToken(type=IconTokenType.delim, value=".")
            continue

        if peeked.isdigit():
            yield _consume_number(peekable)
            continue

        if peeked == "+":
            if _is_number(peekable.peek(3)):
                yield _consume_number(peekable)
                continue
            peekable.read(1)
            yield IconToken(type=CSSTokenType.delim, value="+")
            continue

        if peeked == "-":
            peek_3 = peekable.peek(3)

            if _is_number(peek_3):
                yield _consume_number(peekable)
                continue

            if _is_ident_sequence(peek_3):
                yield _consume_ident_like(peekable)
                continue

            peekable.read(1)
            yield IconToken(type=CSSTokenType.delim, value="-")
            continue

        yield IconToken(type=IconTokenType.delim, value=peekable.read(1))

    yield IconToken(type=IconTokenType.eof)


def _consume_whitespace(fp: PeekableTextIO) -> Optional[IconToken]:
    """Consumes as much whitespace as possible"""
    res = ""
    while _is_whitespace(fp.peek(1)):
        res += fp.read(1)

    if res:
        return IconToken(type=IconTokenType.whitespace, value=res)

    return None


def _consume_ident_like(fp: PeekableTextIO) -> Optional[IconToken]:
    string = _consume_ident_sequence(fp)
    if string == "true":
        return IconToken(type=IconTokenType.true_literal, value=None)
    if string == "false":
        return IconToken(type=IconTokenType.false_literal, value=None)
    if string == "null":
        return IconToken(type=IconTokenType.null_literal, value=None)
    return IconToken(type=IconTokenType.identifier, value=string)


def _consume_comment(fp: PeekableTextIO) -> Optional[IconToken]:
    peek_2 = fp.peek(2)
    if peek_2 is None or len(peek_2) < 2:
        return None
    if peek_2 != "//":
        return None
    fp.read(2)

    res = ""
    while consumed := fp.read(1):
        if consumed == "\n":
            break
        res += consumed

    return IconToken(type=IconTokenType.comment, value=res)


def _consume_string(fp: PeekableTextIO) -> Optional[IconToken]:
    res = _consume_css_string(fp)
    if res is None:
        return None
    if res["type"] == CSSTokenType.bad_string:
        return IconToken(type=IconTokenType.bad_string, value=res["value"])
    return IconToken(type=IconTokenType.string_literal, value=res["value"])


def _consume_number(fp: PeekableTextIO) -> Optional[IconToken]:
    res = _consume_css_number(fp)
    if res is None:
        return None

    return IconToken(type=IconTokenType.number_literal, value=res[0])


WHITESPACE_CHARACTERS = "\n\t "


def _is_whitespace(char: Optional[str]) -> bool:
    return (
        char is not None
        and char != ""
        and all(c in WHITESPACE_CHARACTERS for c in char)
    )
