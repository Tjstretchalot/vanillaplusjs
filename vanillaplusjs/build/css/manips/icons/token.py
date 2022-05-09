from typing import TypedDict, Optional, Union
from enum import Enum


class IconTokenType(str, Enum):
    """The types of tokens that can be encountered when tokenizing the
    args list for the css preprocessor icon command.
    """

    whitespace = "Whitespace"
    """Value corresponds to the original whitespace with newlines standardized"""
    comment = "Comment"
    """Value corresponds to the original comment"""
    open_curly_bracket = "OpenCurlyBracket"
    """Value is None"""
    close_curly_bracket = "CloseCurlyBracket"
    """Value is None"""
    open_square_bracket = "OpenSquareBracket"
    """Value is None"""
    close_square_bracket = "CloseSquareBracket"
    """Value is None"""
    comma = "Comma"
    """Value is None"""
    colon = "Colon"
    """Value is None"""
    string_literal = "StringLiteral"
    """Value corresponds to the original string literal"""
    bad_string = "BadString"
    """Value corresponds to the contents of the malformed string"""
    number_literal = "NumberLiteral"
    """Value corresponds to the original number literal"""
    true_literal = "TrueLiteral"
    """Value is None"""
    false_literal = "FalseLiteral"
    """Value is None"""
    null_literal = "NullLiteral"
    """Value is None"""
    identifier = "Identifier"
    """Value corresponds to the original identifier"""
    delim = "Delim"
    """Value corresponds to the original delimiter"""
    eof = "EOF"
    """Value is None"""


class IconToken(TypedDict):
    """A token when tokenizing the args list for the css preprocessor icon
    command.
    """

    type: IconTokenType
    """The type of the token."""

    value: Optional[Union[str, int, float]]
    """The value of the token, depends on its type"""
