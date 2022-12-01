from typing import Iterable, Union
from vanillaplusjs.build.js.token import JSToken, JSTokenType, JSTokenWithExtra
from vanillaplusjs.build.css.serializer import serialize_string_auto_quote


def serialize(token: Union[JSToken, JSTokenWithExtra]) -> str:
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
        cleaned = token["value"].replace("*/", "*\\/")
        return f"/*{cleaned}*/"
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
        return serialize_string_auto_quote(token["value"])
    elif token["type"] == JSTokenType.regex:
        return f"/{token['value']}/{token['extra']}"
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
