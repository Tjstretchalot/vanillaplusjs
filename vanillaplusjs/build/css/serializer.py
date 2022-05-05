from typing import Iterable
from .token import CSSToken, CSSTokenType


def serialize(token: CSSToken) -> str:
    """Serializes the given CSS token. Attempts to follow the suggestions made
    by https://www.w3.org/TR/css-syntax-3/#serialization

    Args:
        token (CSSToken): The token to serialize

    Returns:
        str: The serialized token
    """
    if token["type"] == CSSTokenType.whitespace:
        return token["value"]
    elif token["type"] == CSSTokenType.string:
        if '"' not in token["value"]:
            return _serialize_string(token["value"], '"')
        elif "'" not in token["value"]:
            return _serialize_string(token["value"], "'")
        return _serialize_string(token["value"], '"')
    elif token["type"] == CSSTokenType.bad_string:
        return '"\n'
    elif token["type"] == CSSTokenType.hash:
        return "#" + token["value"]
    elif token["type"] == CSSTokenType.delim:
        return token["value"]
    elif token["type"] == CSSTokenType.left_parens:
        return "("
    elif token["type"] == CSSTokenType.right_parens:
        return ")"
    elif token["type"] == CSSTokenType.number:
        return str(token["value"])
    elif token["type"] == CSSTokenType.percentage:
        return str(token["value"]) + "%"
    elif token["type"] == CSSTokenType.dimension:
        return str(token["value"]) + token["unit"]
    elif token["type"] == CSSTokenType.comma:
        return ","
    elif token["type"] == CSSTokenType.cdc:
        return "-->"
    elif token["type"] == CSSTokenType.ident:
        return token["value"]
    elif token["type"] == CSSTokenType.function:
        return token["value"] + "("
    elif token["type"] == CSSTokenType.url:
        return (
            "url("
            + _serialize_string(
                token["value"], quote="", simple_escape_characters=('"', "'", "(", "\\")
            )
            + ")"
        )
    elif token["type"] == CSSTokenType.bad_url:
        return "url(()"
    elif token["type"] == CSSTokenType.colon:
        return ":"
    elif token["type"] == CSSTokenType.semicolon:
        return ";"
    elif token["type"] == CSSTokenType.cdo:
        return "<!--"
    elif token["type"] == CSSTokenType.at_keyword:
        return "@" + token["value"]
    elif token["type"] == CSSTokenType.left_square_bracket:
        return "["
    elif token["type"] == CSSTokenType.right_square_bracket:
        return "]"
    elif token["type"] == CSSTokenType.left_curly_bracket:
        return "{"
    elif token["type"] == CSSTokenType.right_curly_bracket:
        return "}"
    elif token["type"] == CSSTokenType.comment:
        return "/*" + token["value"] + "*/"
    elif token["type"] == CSSTokenType.eof:
        return ""

    raise ValueError("Unknown token type: " + repr(token["type"]))


def serialize_many(token: Iterable[CSSToken]) -> str:
    """Serializes the given CSS tokens."""
    return "".join(serialize(t) for t in token)


def _serialize_string(string: str, quote: str, simple_escape_characters=("\\",)) -> str:
    """Serializes the given string, using the given quote character."""
    res = quote
    for char in string:
        if char == quote or char in simple_escape_characters:
            res += "\\" + char
            continue

        char_ord = ord(char)
        if (
            0 <= char_ord <= 8
            or char_ord == 0x000B
            or 0x000E <= char_ord <= 0x001F
            or char_ord >= 0x007F
        ):
            res += "\\" + hex(char_ord)[2:]
            continue

        res += char
    res += quote
    return res
