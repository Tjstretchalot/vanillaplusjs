from typing import Generator, List, Literal, Optional, Union

from vanillaplusjs.build.css.manips.icons.settings import ButtonSetting, ButtonSettings
from .token import IconTokenType, IconToken
from .command import IconCommand


def parse_icon_command() -> Generator[None, IconToken, IconCommand]:
    """Parses the tokens sent to this function, returning the icon
    command, if a valid icon command was constructed from the tokens,
    otherwise raises ValueError with the error message.

    Yields:
        None

    Sends:
        IconToken: the next token

    Returns:
        IconCommand: the icon command

    Raises:
        ValueError: if the tokens do not form a valid icon command
    """
    token = yield from next_significant_token()
    if token["type"] != IconTokenType.identifier:
        raise ValueError(f"expected icon identifier, got {token}")

    icon_name = token["value"]

    token = yield from next_significant_token()
    if token["type"] != IconTokenType.identifier:
        raise ValueError(f"expected icon initial color, got {token}")

    icon_initial_color = token["value"]

    token = yield from next_significant_token()
    icon_colors: Optional[List[str]] = None
    if token["type"] == IconTokenType.open_square_bracket:
        icon_colors = yield from consume_string_literal_list()
    else:
        if token["type"] != IconTokenType.identifier or token["value"] != "all-colors":
            raise ValueError(f"expected icon colors, got {token}")

    token = yield from next_significant_token()
    icon_sizes: Optional[List[str]] = None
    if token["type"] == IconTokenType.open_square_bracket:
        icon_sizes = yield from consume_string_literal_list()
    else:
        if token["type"] != IconTokenType.identifier or token["value"] != "all-sizes":
            raise ValueError(f"expected icon sizes, got {token}")

    token = yield from next_significant_token()
    if token["type"] == IconTokenType.eof:
        return IconCommand(
            icon_name=icon_name,
            icon_initial_color=icon_initial_color,
            output_colors=icon_colors,
            output_sizes=icon_sizes,
            button="default",
        )

    button_settings: Optional[Union[Literal["default"], ButtonSettings]] = "default"
    if token["type"] == IconTokenType.open_curly_bracket:
        button_settings = yield from consume_button_settings()
    elif token["type"] == IconTokenType.identifier:
        if token["value"] == "no-btn":
            button_settings = None
        elif token["value"] in ("btn", "default"):
            button_settings = "default"
        else:
            raise ValueError(f"expected button settings, got {token}")
    else:
        raise ValueError(f"expected button settings, got {token}")

    return IconCommand(
        icon_name=icon_name,
        icon_initial_color=icon_initial_color,
        output_colors=icon_colors,
        output_sizes=icon_sizes,
        button=button_settings,
    )


def next_significant_token() -> Generator[None, IconToken, IconToken]:
    """Gets the next significant token from the stream. This
    skips over whitespace and comments.
    """
    token = yield
    while token["type"] in (IconTokenType.comment, IconTokenType.whitespace):
        token = yield
    return token


def consume_string_literal_list() -> Generator[None, IconToken, List[str]]:
    """Consumes a list of string literals from the stream,
    raising ValueError if the tokens do not form a valid list.

    Assumes that the opening square bracket has already been
    consumed.

    Yields:
        None

    Sends:
        IconToken: the next token

    Returns:
        List[str]: the list of string literals
    """
    strings = []
    need_comma = False
    while True:
        token = yield from next_significant_token()
        if token["type"] == IconTokenType.close_square_bracket:
            return strings

        if need_comma:
            if token["type"] != IconTokenType.comma:
                raise ValueError(f"expected comma, got {token}")
            need_comma = False
            continue

        if token["type"] != IconTokenType.string_literal:
            raise ValueError(f"expected string literal, got {token}")

        strings.append(token["value"])
        need_comma = True


def consume_button_settings() -> Generator[None, IconToken, ButtonSettings]:
    """Consumes a button settings from the stream,
    raising ValueError if the tokens do not form a valid button settings.

    Assumes that the opening curly bracket has already been
    consumed.

    Yields:
        None

    Sends:
        IconToken: the next token

    Returns:
        ButtonSettings: the button settings
    """
    button_settings = ButtonSettings(default_button=None, button_by_identifier=dict())

    need_comma = False
    while True:
        token = yield from next_significant_token()
        if token["type"] == IconTokenType.close_curly_bracket:
            return button_settings

        if need_comma:
            if token["type"] != IconTokenType.comma:
                raise ValueError(f"expected comma, got {token}")
            need_comma = False
            continue

        if token["type"] != IconTokenType.string_literal:
            raise ValueError(f"expected string literal, got {token}")

        button_name = token["value"]

        token = yield from next_significant_token()
        if token["type"] != IconTokenType.colon:
            raise ValueError(f"expected colon, got {token}")

        token = yield from next_significant_token()
        if token["type"] != IconTokenType.open_square_bracket:
            raise ValueError(f"expected open square bracket, got {token}")

        button_colors = yield from consume_string_literal_list()
        if len(button_colors) != 3:
            raise ValueError(f"expected 3 colors, got {len(button_colors)}")

        if button_name == "default":
            button_settings.default_button = ButtonSetting(
                active_color=button_colors[0],
                hover_color=button_colors[1],
                disabled_color=button_colors[2],
            )
        else:
            button_settings.button_by_identifier[button_name] = ButtonSetting(
                active_color=button_colors[0],
                hover_color=button_colors[1],
                disabled_color=button_colors[2],
            )

        need_comma = True
