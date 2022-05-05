"""Describes a token within the CSS tree. We would like to walk and manipulate
the tokens that form the CSS tree and not the tree itself, since manipulating
entire AST nodes is usually either slow or difficult to nest. Furthermore, we
want parity with how we are manipulating the HTML tree.

If we use tinycss2 it doesn't support tree walkers, but adding tree walkers
is nearly as much work as just tokenizing ourself. Our tokenizer follows the
CSS3 spec.
"""
from typing import Optional, TypedDict, Union
from enum import Enum


class CSSTokenType(str, Enum):
    """The possible token types we can encounter."""

    whitespace = "Whitespace"
    string = "String"
    bad_string = "BadString"
    hash = "Hash"
    delim = "Delim"
    left_parens = "LeftParenthesis"
    right_parens = "RightParenthesis"
    number = "Number"
    percentage = "Percentage"
    dimension = "Dimension"
    comma = "Comma"
    cdc = "CDC"
    """refers to -->"""
    ident = "Ident"
    function = "Function"
    url = "URL"
    bad_url = "BadURL"
    colon = "Colon"
    semicolon = "Semicolon"
    cdo = "CDO"
    """refers to <!--"""
    at_keyword = "AtKeyword"
    left_square_bracket = "LeftSquareBracket"
    right_square_bracket = "RightSquareBracket"
    left_curly_bracket = "LeftCurlyBracket"
    right_curly_bracket = "RightCurlyBracket"
    eof = "EOF"

    # DIFFERENT FROM SPEC
    comment = "Comment"
    """A comment. The value of the comment is text of the comment immediately
    after the start of comment (/*) and before the end of comment (*/). The
    comment is parsed as if by https://www.w3.org/TR/css-syntax-3/#consume-comments
    except with the value stored as this preprocessor uses semantic comments.
    Example:

    /* foo */
    has a value ' foo '
    """


class CSSToken(TypedDict):
    """A token within the CSS tree."""

    type: CSSTokenType
    """The type of the token."""

    value: Optional[Union[str, int, float]]
    """The value for the token. This will follow the description in the
    css syntax spec description for the value. If no value is specified
    then this will be None.
    """

    type_flag: Optional[str]
    """Some tokens may have a type flag. In particular, number, percentage, and
    dimension tokens have the type flag either as 'integer' or 'number'. If the
    type has a type flag but it is unset, assume 'integer'


    The hash tokens may have a type flag set to 'id', and only such
    hash tokens are valid id selectors.
    """

    unit: Optional[str]
    """The dimension token may have the unit set to one or more
    code points. In all other cases, the unit is None or unset
    """
