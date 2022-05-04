"""Describes the interface that must be implemented for a component which
manipulates the dom.
"""
from typing import Dict, Optional, Tuple, Type, TypedDict, Union


class HTMLToken(TypedDict):
    """Describes a token that is encountered while walking an html
    document
    """

    type: str
    """The type of token, as a CamelCase string, e.g., StartTag.
    This is always a key in html5lib.constants.tokenTypes
    """

    name: Optional[str]
    """The name of the tag; always omitted if the token type is
    not a tag token type (StartTag, EndTag, EmptyTag)
    """

    data: Optional[Union[Dict[Tuple[Type[None], str], str], str]]
    """If this is a StartTag token, this corresponds to a dictionary
    where the keys are of the form (None, str) and the values are str. The None
    in the tuple refers to the namespace of the attribute, which is always None
    for valid html.

    If this is a Comment token, this corresponds to the contents of the comment
    as text, i.e., a str.

    If this is a SpaceCharacters or Characters token, this corresponds to those
    characters, i.e., a str
    """


def start_tag(name: str, attributes: Dict[str, str]) -> HTMLToken:
    """Creates a start tag token"""
    return {
        "type": "StartTag",
        "name": name,
        "data": dict(((None, key), value) for key, value in attributes.items()),
    }


def end_tag(name: str) -> HTMLToken:
    """Creates an end tag token"""
    return {"type": "EndTag", "name": name}


def empty_tag(name: str, attributes: Dict[str, str]) -> HTMLToken:
    """Creates an empty tag token"""
    return {
        "type": "EmptyTag",
        "name": name,
        "data": dict(((None, key), value) for key, value in attributes.items()),
    }


def characters(text: str) -> HTMLToken:
    """Creates a characters token"""
    return {"type": "Characters", "data": text}


def space_characters(text: str) -> HTMLToken:
    """Creates a space characters token"""
    return {"type": "SpaceCharacters", "data": text}
