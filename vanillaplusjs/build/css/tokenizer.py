"""Our simple css tokenizer, following https://www.w3.org/TR/css-syntax-3/.
Specifically, this implements the consume token section:
https://www.w3.org/TR/css-syntax-3/#consume-token
"""
from io import TextIOBase
from typing import Generator, Literal, Optional, Tuple, Union
from .token import CSSToken, CSSTokenType
from vanillaplusjs.build.ioutil import PreprocessedTextIO, PeekableTextIO


def tokenize(fp: TextIOBase) -> Generator[CSSToken, None, None]:
    """Tokenizes the given file-like object, streaming back the
    tokens as they are parsed.

    Follows https://www.w3.org/TR/css-syntax-3/#consume-token

    Args:
        fp (FileIO): a file-like object to parse

    Yields:
        CSSToken: the next token

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

        if (whitespace := _consume_whitespace(peekable)) is not None:
            yield whitespace
            continue

        if peeked == '"':
            yield _consume_string(peekable)
            continue

        if peeked == "#":
            peekable.read(1)
            peek_2 = peekable.peek(2)
            if len(peek_2) == 0:
                yield CSSToken(type=CSSTokenType.delim, value="#")
                continue

            if _is_ident_codepoint(peek_2[0]) or _is_valid_escape(peek_2):
                res = CSSToken(type=CSSTokenType.hash)
                if _is_ident_sequence(peekable.peek(3)):
                    res["type_flag"] = "id"
                else:
                    res["type_flag"] = "unrestricted"
                res["value"] = _consume_ident_sequence(peekable)
                yield res
                continue

            yield CSSToken(type=CSSTokenType.delim, value="#")
            continue

        if peeked == "'":
            yield _consume_string(peekable)
            continue

        if peeked == "(":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.left_parens)
            continue

        if peeked == ")":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.right_parens)
            continue

        if peeked == "+":
            if _is_number(peekable.peek(3)):
                yield _consume_numeric_token(peekable)
                continue
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.delim, value="+")
            continue

        if peeked == ",":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.comma)
            continue

        if peeked == "-":
            peek_3 = peekable.peek(3)

            if _is_number(peek_3):
                yield _consume_numeric_token(peekable)
                continue

            if len(peek_3) == 3 and peek_3 == "-->":
                peekable.read(3)
                yield CSSToken(type=CSSTokenType.cdc)
                continue

            if _is_ident_sequence(peek_3):
                yield _consume_ident_like(peekable)
                continue

            peekable.read(1)
            yield CSSToken(type=CSSTokenType.delim, value="-")
            continue

        if peeked == ".":
            if _is_number(peekable.peek(3)):
                yield _consume_numeric_token(peekable)
                continue

            peekable.read(1)
            yield CSSToken(type=CSSTokenType.delim, value=".")
            continue

        if peeked == ":":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.colon)
            continue

        if peeked == ";":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.semicolon)
            continue

        if peeked == "<":
            if peekable.peek(4) == "<!--":
                peekable.read(4)
                yield CSSToken(type=CSSTokenType.cdo)
                continue
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.delim, value="<")
            continue

        if peeked == "@":
            peekable.read(1)
            if _is_ident_sequence(peekable.peek(3)):
                value = _consume_ident_sequence(peekable)
                yield CSSToken(type=CSSTokenType.at_keyword, value=value)
                continue
            yield CSSToken(type=CSSTokenType.delim, value="@")
            continue

        if peeked == "[":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.left_square_bracket)
            continue

        if peeked == "\\":
            if _is_valid_escape(peekable.peek(2)):
                yield _consume_ident_like(peekable)
                continue
            # parse error
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.delim, value="\\")
            continue

        if peeked == "]":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.right_square_bracket)
            continue

        if peeked == "{":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.left_curly_bracket)
            continue

        if peeked == "}":
            peekable.read(1)
            yield CSSToken(type=CSSTokenType.right_curly_bracket)
            continue

        if peeked.isdigit():
            yield _consume_numeric_token(peekable)
            continue

        if _is_ident_start_codepoint(peeked):
            yield _consume_ident_like(peekable)
            continue

        peekable.read(1)
        yield CSSToken(type=CSSTokenType.delim, value=peeked)

    yield CSSToken(type=CSSTokenType.eof)


def tokenize_and_close(fp: TextIOBase) -> Generator[CSSToken, None, None]:
    """The same as tokenize, except at the end it closes the file handle"""
    try:
        yield from tokenize(fp)
    finally:
        fp.close()


def _consume_comment(fp: PreprocessedTextIO) -> Optional[CSSToken]:
    """https://www.w3.org/TR/css-syntax-3/#consume-comments

    Unlike as defined in the spec, this will return a Comment token
    whose value corresponds to the value of the comment excluding the
    comment markers.
    """
    peeked = fp.peek(2)
    if peeked != "/*":
        return None

    fp.read(2)
    comment = ""
    while True:
        peeked = fp.peek(2)
        if peeked is None:
            return None
        if peeked == "*/":
            fp.read(2)
            return CSSToken(type=CSSTokenType.comment, value=comment)
        comment += fp.read(1)


WHITESPACE_CHARACTERS = "\n\t "


def _consume_whitespace(fp: PreprocessedTextIO) -> Optional[CSSToken]:
    """Consumes as much https://www.w3.org/TR/css-syntax-3/#whitespace
    as possible
    """
    res = ""
    while _is_whitespace(fp.peek(1)):
        res += fp.read(1)

    if res:
        return CSSToken(type=CSSTokenType.whitespace, value=res)

    return None


def _consume_string(
    fp: PreprocessedTextIO, ending_code_point: Optional[str] = None
) -> Optional[CSSToken]:
    """https://www.w3.org/TR/css-syntax-3/#consume-a-string-token

    Unlike as specified, if you do not specify an ending code point,
    you MUST NOT have consumed the opening quote.
    """
    if ending_code_point is None:
        ending_code_point = fp.read(1)

    value = ""
    while True:
        peeked = fp.peek(1)
        if peeked is None:
            return CSSToken(type=CSSTokenType.string, value=value)

        if peeked == ending_code_point:
            fp.read(1)
            return CSSToken(type=CSSTokenType.string, value=value)

        if peeked == "\n":
            return CSSToken(type=CSSTokenType.bad_string, value=value)

        if peeked == "\\":
            peek_2 = fp.peek(2)
            if len(peek_2) == 1:
                fp.read(1)
                continue

            if peek_2[1] == "\n":
                fp.read(2)
                continue

            fp.read(1)
            value += _consume_escaped_code_point(fp)
            continue

        value += fp.read(1)


def _consume_escaped_code_point(fp: PreprocessedTextIO) -> Optional[str]:
    """https://www.w3.org/TR/css-syntax-3/#consume-escaped-code-point"""
    first_char = fp.peek(1)
    if _is_hex_digit(first_char):
        hex_digits = fp.read(1)
        while len(hex_digits) < 6 and _is_hex_digit(fp.peek(1)):
            hex_digits += fp.read(1)

        if _is_whitespace(fp.peek(1)):
            fp.read(1)

        hex_num = int(hex_digits, 16)
        if hex_num == 0 or 0xD800 <= hex_num <= 0xDFFF or hex_num > 0x10FFFF:
            return "\uFFFD"
        return chr(hex_num)

    if first_char is None:
        return "\uFFFD"

    return fp.read(1)


def _consume_ident_sequence(fp: PreprocessedTextIO) -> str:
    """https://www.w3.org/TR/css-syntax-3/#consume-an-ident-sequence"""
    result = ""
    while (peeked := fp.peek(1)) is not None:
        if _is_ident_codepoint(peeked):
            result += fp.read(1)
            continue

        if _is_valid_escape(fp.peek(2)):
            fp.read(1)
            result += _consume_escaped_code_point(fp)
            continue

        break

    return result


def _consume_number(
    fp: PreprocessedTextIO,
) -> Optional[Tuple[Union[int, float], Literal["integer', 'number"]]]:
    """Consumes a number

    https://www.w3.org/TR/css-syntax-3/#consume-a-number
    """
    res_type = "integer"
    repr = ""

    peeked = fp.peek(1)
    if peeked is None or peeked == "":
        return None

    if peeked in "+-":
        repr += fp.read(1)

    while True:
        peeked = fp.peek(1)
        if peeked is None:
            if repr in "+-" or repr == "":
                return None
            return int(repr), res_type
        if not peeked.isdigit():
            break
        repr += fp.read(1)

    peek_2 = fp.peek(2)
    if peek_2 is None or len(peek_2) < 2:
        return int(repr), res_type

    if peek_2[0] == "." and peek_2[1].isdigit():
        repr += fp.read(2)
        res_type = "number"
        while True:
            peeked = fp.peek(1)
            if peeked is None:
                return float(repr), res_type
            if not peeked.isdigit():
                break
            repr += fp.read(1)

    peek_3 = fp.peek(3)
    if peek_3 is None or len(peek_3) < 2:
        return float(repr), res_type

    if peek_3[0] in "eE" and (
        peek_3[1].isdigit()
        or (peek_3[1] in "+-" and len(peek_3) == 3 and peek_3[2].isdigit())
    ):
        res_type = "number"
        repr += fp.read(2)
        while True:
            peeked = fp.peek(1)
            if peeked is None:
                return float(repr), res_type
            if not peeked.isdigit():
                break
            repr += fp.read(1)

    if res_type == "integer":
        return int(repr), res_type
    return float(repr), res_type


def _consume_numeric_token(fp: PreprocessedTextIO) -> Optional[CSSToken]:
    """Consumes a numeric token; returns either a number token, percentage token,
    or a dimension token.
    https://www.w3.org/TR/css-syntax-3/#consume-a-numeric-token
    """
    number_value, number_type = _consume_number(fp)

    if _is_ident_sequence(fp.peek(3)):
        return CSSToken(
            type=CSSTokenType.dimension,
            value=number_value,
            type_flag=number_type,
            unit=_consume_ident_sequence(fp),
        )

    if fp.peek(1) == "%":
        fp.read(1)
        return CSSToken(
            type=CSSTokenType.percentage,
            value=number_value,
            type_flag=number_type,
        )

    return CSSToken(
        type=CSSTokenType.number,
        value=number_value,
        type_flag=number_type,
    )


def _consume_ident_like(fp: PreprocessedTextIO) -> Optional[CSSToken]:
    """Consumes an ident-like token

    https://www.w3.org/TR/css-syntax-3/#consume-an-ident-like-token
    """
    string = _consume_ident_sequence(fp)
    if len(string) == 3 and string.lower() == "url" and fp.peek(1) == "(":
        fp.read(1)
        while True:
            peek_2 = fp.peek(2)
            if peek_2 is None or len(peek_2) < 2 or not _is_whitespace(peek_2):
                break
            fp.read(1)

        peek_2 = fp.peek(2)
        if peek_2 is None or peek_2 == "":
            return CSSToken(type=CSSTokenType.ident, value=string)
        if peek_2[0] in ('"', "'") or (
            len(peek_2) == 2 and _is_whitespace(peek_2[0]) and peek_2[1] in ('"', "'")
        ):
            return CSSTokenType(type=CSSTokenType.function, value=string)

        return _consume_url(fp)

    if fp.peek(1) == "(":
        fp.read(1)
        return CSSToken(type=CSSTokenType.function, value=string)

    return CSSToken(type=CSSTokenType.ident, value=string)


def _consume_url(fp: PreprocessedTextIO) -> Optional[CSSToken]:
    """Consumes a URL token. Assumes that the initial url( has already been consumed.
    This also is for consuming an _unquoted_ URL; a quoted url should be parsed as
    a function token. This is only called via consume an ident-like token.

    https://www.w3.org/TR/css-syntax-3/#consume-a-url-token
    """
    value = ""
    while True:
        peeked = fp.peek(1)
        if peeked is None or peeked == "":
            # parse error
            return CSSToken(type=CSSTokenType.url, value=value)

        if peeked == ")":
            fp.read(1)
            return CSSToken(type=CSSTokenType.url, value=value)

        if _is_whitespace(peeked):
            fp.read(1)
            continue

        if peeked in ('"', "'", "(") or _is_non_printable(peeked):
            _consume_remnants_of_bad_url(fp)
            return CSSToken(type=CSSTokenType.bad_url)

        if peeked == "\\" and _is_valid_escape(fp.peek(2)):
            fp.read(1)
            value += _consume_escaped_code_point(fp)
            continue

        value += fp.read(1)


def _consume_remnants_of_bad_url(fp: PreprocessedTextIO) -> None:
    """Consumes the remnants of a bad URL
    https://www.w3.org/TR/css-syntax-3/#consume-the-remnants-of-a-bad-url
    """
    while True:
        consumed = fp.read(1)
        if consumed is None or consumed == "" or consumed == ")":
            return

        if _is_valid_escape(consumed + fp.peek(1)):
            _consume_escaped_code_point(fp)
            continue


HEX_CHARACTERS = "0123456789abcdefABCDEF"


def _is_hex_digit(char: str) -> bool:
    return char is not None and char in HEX_CHARACTERS


def _is_whitespace(char: Optional[str]) -> bool:
    return (
        char is not None
        and char != ""
        and all(c in WHITESPACE_CHARACTERS for c in char)
    )


def _is_ident_start_codepoint(char: Optional[str]) -> bool:
    if char is None:
        return False
    return char.isalpha() or ord(char) >= 0x0080 or char == "_"


def _is_ident_codepoint(char: Optional[str]) -> bool:
    if char is None:
        return False
    return _is_ident_start_codepoint(char) or char.isdigit() or char == "-"


def _is_valid_escape(two: str) -> bool:
    """Determines if the given two characters form a valid escape
    https://www.w3.org/TR/css-syntax-3/#check-if-two-code-points-are-a-valid-escape

    This does not support being called without the two characters
    """
    if len(two) != 2:
        return False

    return two[0] == "\\" and two[1] != "\n"


def _is_ident_sequence(three: str) -> bool:
    """Determines if the given three characters would start an
    ident sequence

    https://www.w3.org/TR/css-syntax-3/#check-if-three-code-points-would-start-an-ident-sequence

    This does not support being called without the three characters
    """
    if len(three) != 3:
        return False

    if three[0] == "-":
        return (
            _is_ident_start_codepoint(three[1])
            or three[1] == "-"
            or _is_valid_escape(three[1:])
        )

    if _is_ident_start_codepoint(three[0]):
        return True

    if three[0] == "\\":
        return _is_valid_escape(three[0:2])

    return False


def _is_number(three: Optional[str]) -> bool:
    """Determines if the given three codepoints would start a number
    https://www.w3.org/TR/css-syntax-3/#check-if-three-code-points-would-start-a-number
    """
    if three is None:
        return False
    if len(three) != 3:
        return False

    if three[0] in "+-":
        return three[1].isdigit() or (three[1] == "." and three[2].isdigit())

    if three[0] == ".":
        return three[1].isdigit()

    return three[0].isdigit()


def _is_non_printable(char: Optional[str]) -> bool:
    """https://www.w3.org/TR/css-syntax-3/#non-printable-code-point"""
    if char is None or char == "":
        return False

    char_ord = ord(char)
    return (
        0 <= char_ord <= 8
        or char_ord == 0x000B
        or 0x000E <= char_ord <= 0x001F
        or char_ord == 0x007F
    )
