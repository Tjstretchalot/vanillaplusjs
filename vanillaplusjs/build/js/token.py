"""Describes a token in a javascript document. For our purposes we do not need
a complete lexer; the ecmascript specification is rather hard to follow
(https://tc39.es/ecma262/#sec-ecmascript-language-source-code). So we will
only consider the tokens necessary to identify import statements in a series
of import statements at the top of the file.
"""
from typing import Optional, TypedDict
from enum import Enum


class JSTokenType(str, Enum):
    """The tokens that can be produced by the tokenizer"""

    whitespace = "Whitespace"
    """Value is the matched whitespace"""
    line_terminator = "LineTerminator"
    """Value is None"""
    comment = "Comment"
    """Vaue is the matched comment text, not including the comment marker. For
    single-line comments, the comment does not include the line terminator.
    """
    open_curly_bracket = "OpenCurlyBracket"
    """Value is None"""
    close_curly_bracket = "CloseCurlyBracket"
    """Value is None"""
    asterisk = "Asterisk"
    """Value is None"""
    keyword_as = "as"
    """Value is None"""
    keyword_import = "import"
    """Value is None"""
    keyword_from = "from"
    """Value is None"""
    comma = "Comma"
    """Value is None"""
    identifier = "Identifier"
    """Value is the matched identifier"""
    string_literal = "StringLiteral"
    """Value is the contents of the matched string literal"""
    semicolon = "Semicolon"
    """Value is None"""

    # DIFFERENT FROM SPEC
    regex = "RegularExpressionLiteral"
    """Value is the contents of the matched regular expression literal, e.g., for /\g/, the value is '\\g'
    The `extra` field contains the flags, if any. so for /foo/g, the value is 'foo' and the extra is 'g'
    """
    invalid = "Invalid"
    """Value is the contents of the invalid token"""
    eof = "EOF"
    """Value is None"""


class JSToken(TypedDict):

    type: JSTokenType
    """The type of the token."""

    value: Optional[str]
    """The value for the token. See JSTokenType for value definitions
    """


class JSTokenWithExtra(TypedDict):

    type: JSTokenType
    """The type of the token."""

    value: Optional[str]
    """The value for the token. See JSTokenType for value definitions
    """

    extra: Optional[str]
    """Extra information about the token."""
