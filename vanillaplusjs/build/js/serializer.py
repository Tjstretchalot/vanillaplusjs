from typing import Iterable
from .token import JSToken, JSTokenType


def serialize(token: JSToken) -> str:
    """Serializes the given JS token.

    Args:
        token (JSToken): The token to serialize

    Returns:
        str: The serialized token
    """
    if token["type"] == JSTokenType.whitespace:
        return token["value"]
    elif token["type"] == JSTokenType.line_terminator:
        return "\n"
    elif token["type"] == JSTokenType.comment:
        return f'/*{token["value"]}*/'
    elif token["type"] == JSTokenType.open_curly_bracket:
        return "{"
    elif token["type"] == JSTokenType.close_curly_bracket:
        return "}"
    elif token["type"] == JSTokenType.asterisk:
        return "*"
    elif token["type"] == JSTokenType.keyword_as:
        return "as"
    elif token["type"] == JSTokenType.keyword_import:
        return "import"
    elif token["type"] == JSTokenType.keyword_from:
        return "from"
    elif token["type"] == JSTokenType.comma:
        return ","
    elif token["type"] == JSTokenType.identifier:
        return token["value"]
    elif token["type"] == JSTokenType.string_literal:
        return f'"{token["value"]}"'
    elif token["type"] == JSTokenType.semicolon:
        return ";"
    elif token["type"] == JSTokenType.invalid:
        return token["value"]
    elif token["type"] == JSTokenType.eof:
        return ""

    raise ValueError("Unknown token type: " + repr(token["type"]))


def serialize_many(token: Iterable[JSToken]) -> str:
    """Serializes the given JS tokens."""
    return "".join(serialize(t) for t in token)
