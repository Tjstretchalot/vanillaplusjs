import dataclasses
from typing import Dict, List, Optional
from vanillaplusjs.build.build_context import BuildContext
from .color import Color
import json
import os
from vanillaplusjs.build.css.token import CSSToken, CSSTokenType
from vanillaplusjs.build.css.tokenizer import tokenize
import string


@dataclasses.dataclass
class ButtonSetting:
    """The settings for a single export of a button from the icon file"""

    active_color: str
    """The color when the button is not hovered or disabled"""

    hover_color: str
    """The color when the button is hovered and not disabled"""

    disabled_color: str
    """The color when the button is disabled"""


@dataclasses.dataclass
class ButtonSettings:
    """Describes the various buttons to export for an icon."""

    default_button: Optional[ButtonSetting]
    """The unprefixed button settings; i.e., if the icon name is "circle",
    this is the settings for .icon-btn-circle-(size)
    """

    button_by_identifier: Dict[str, ButtonSetting]
    """The button settings for each button identifier. May be empty."""


@dataclasses.dataclass
class IconSettings:
    """Describes the context for which we are processing an icon command;
    this is information that is gathered from the :root prelude on the
    qualified rule in `main.css`, plus `vanillaplusjs.json`
    """

    color_map: Dict[str, Color]
    """The color map for the icon command."""

    sizes: List[str]
    """The sizes available for the icon command."""

    default_button: Optional[ButtonSettings]
    """The default button settings for icons, or None if by default
    we do not export buttons.
    """


def load_icon_settings(context: BuildContext) -> IconSettings:
    """Loads the icon settings from the given build context."""
    with open(context.config_file, "r") as f:
        config: dict = json.load(f)

    button_settings: ButtonSettings = ButtonSettings(
        default_button=ButtonSetting(
            active_color="primary",
            hover_color="primary-dark",
            disabled_color="disabled",
        ),
        button_by_identifier=dict(),
    )
    icons: Optional[dict] = config.get("icons")
    if icons is not None:
        default_button: Optional[dict] = icons.get(
            "default_button",
            {},
        )
        if default_button is None:
            button_settings = dataclasses.replace(button_settings, default_button=None)
        else:
            active_color: Optional[str] = default_button.get(
                "active_color", button_settings.default_button.active_color
            )
            hover_color: Optional[str] = default_button.get(
                "hover_color", button_settings.default_button.hover_color
            )
            disabled_color: Optional[str] = default_button.get(
                "disabled_color", button_settings.default_button.disabled_color
            )
            if (
                active_color is not None
                and hover_color is not None
                and disabled_color is not None
            ):
                button_settings = dataclasses.replace(
                    button_settings,
                    default_button=ButtonSetting(
                        active_color=active_color,
                        hover_color=hover_color,
                        disabled_color=disabled_color,
                    ),
                )

        button_by_identifier: Optional[dict[str, dict]] = icons.get(
            "button_by_identifier", dict()
        )
        if button_by_identifier is None:
            button_settings = dataclasses.replace(
                button_settings, button_by_identifier=dict()
            )
        else:
            for button_identifier, button_config in button_by_identifier.items():
                active_color: Optional[str] = button_config.get(
                    "active_color", button_settings.default_button.active_color
                )
                hover_color: Optional[str] = button_config.get(
                    "hover_color", button_settings.default_button.hover_color
                )
                disabled_color: Optional[str] = button_config.get(
                    "disabled_color", button_settings.default_button.disabled_color
                )
                if (
                    active_color is not None
                    and hover_color is not None
                    and disabled_color is not None
                ):
                    button_settings = dataclasses.replace(
                        button_settings,
                        button_by_identifier={
                            **button_settings.button_by_identifier,
                            button_identifier: ButtonSetting(
                                active_color=active_color,
                                hover_color=hover_color,
                                disabled_color=disabled_color,
                            ),
                        },
                    )

    color_map: Dict[str, Color] = dict()
    sizes: List[str] = list()

    if os.path.exists(os.path.join(context.folder, context.default_css_file)):
        with open(os.path.join(context.folder, context.default_css_file), "r") as f:
            gen = tokenize(f)

            def next_significant():
                token = next(gen)
                while token["type"] in (CSSTokenType.whitespace, CSSTokenType.comment):
                    token = next(gen)
                return token

            try:
                token = next_significant()
                while True:
                    if token["type"] == CSSTokenType.left_curly_bracket:
                        nest_level = 1
                        while nest_level > 0:
                            token = next(gen)
                            if token["type"] == CSSTokenType.left_curly_bracket:
                                nest_level += 1
                            elif token["type"] == CSSTokenType.right_curly_bracket:
                                nest_level -= 1
                        token = next(gen)
                        continue

                    if token["type"] != CSSTokenType.colon:
                        token = next_significant()
                        continue

                    token = next_significant()
                    if token["type"] != CSSTokenType.ident or token["value"] != "root":
                        continue

                    token = next_significant()
                    if token["type"] != CSSTokenType.left_curly_bracket:
                        continue
                    break

                # token is the left curly bracket for the :root qualified rule
                token = next_significant()
                while token["type"] != CSSTokenType.right_curly_bracket:
                    if token["type"] != CSSTokenType.ident:
                        # parse error
                        break

                    component_name = token["value"]

                    token = next_significant()
                    if token["type"] != CSSTokenType.colon:
                        # parse error
                        break

                    component_value: List[CSSToken] = [next_significant()]
                    if component_value[0]["type"] == CSSTokenType.function:
                        token = next_significant()
                        while token["type"] != CSSTokenType.right_parens:
                            component_value.append(token)
                            token = next_significant()
                        component_value.append(token)

                    token = next_significant()
                    if token["type"] != CSSTokenType.semicolon:
                        # parse error
                        break
                    token = next_significant()

                    if component_name.startswith("--col-"):
                        color = interpret_as_color(component_value)
                        if color is not None:
                            color_map[component_name[6:]] = color
                    elif component_name.startswith("--icon-size-"):
                        sizes.append(component_name[12:])
            except StopIteration:
                pass
            gen.close()

    return IconSettings(
        default_button=button_settings,
        color_map=color_map,
        sizes=list(dict((s, None) for s in sizes)),  # dict to preserve order
    )


NAMED_CSS_COLORS = {
    "aliceblue": Color(red=240, green=248, blue=255),
    "antiquewhite": Color(red=250, green=235, blue=215),
    "aqua": Color(red=0, green=255, blue=255),
    "aquamarine": Color(red=127, green=255, blue=212),
    "azure": Color(red=240, green=255, blue=255),
    "beige": Color(red=245, green=245, blue=220),
    "bisque": Color(red=255, green=228, blue=196),
    "black": Color(red=0, green=0, blue=0),
    "blanchedalmond": Color(red=255, green=235, blue=205),
    "blue": Color(red=0, green=0, blue=255),
    "blueviolet": Color(red=138, green=43, blue=226),
    "brown": Color(red=165, green=42, blue=42),
    "burlywood": Color(red=222, green=184, blue=135),
    "cadetblue": Color(red=95, green=158, blue=160),
    "chartreuse": Color(red=127, green=255, blue=0),
    "chocolate": Color(red=210, green=105, blue=30),
    "coral": Color(red=255, green=127, blue=80),
    "cornflowerblue": Color(red=100, green=149, blue=237),
    "cornsilk": Color(red=255, green=248, blue=220),
    "crimson": Color(red=220, green=20, blue=60),
    "cyan": Color(red=0, green=255, blue=255),
    "darkblue": Color(red=0, green=0, blue=139),
    "darkcyan": Color(red=0, green=139, blue=139),
    "darkgoldenrod": Color(red=184, green=134, blue=11),
    "darkgray": Color(red=169, green=169, blue=169),
    "darkgreen": Color(red=0, green=100, blue=0),
    "darkkhaki": Color(red=189, green=183, blue=107),
    "darkmagenta": Color(red=139, green=0, blue=139),
    "darkolivegreen": Color(red=85, green=107, blue=47),
    "darkorange": Color(red=255, green=140, blue=0),
    "darkorchid": Color(red=153, green=50, blue=204),
    "darkred": Color(red=139, green=0, blue=0),
    "darksalmon": Color(red=233, green=150, blue=122),
    "darkseagreen": Color(red=143, green=188, blue=143),
    "darkslateblue": Color(red=72, green=61, blue=139),
    "darkslategray": Color(red=47, green=79, blue=79),
    "darkturquoise": Color(red=0, green=206, blue=209),
    "darkviolet": Color(red=148, green=0, blue=211),
    "deeppink": Color(red=255, green=20, blue=147),
    "deepskyblue": Color(red=0, green=191, blue=255),
    "dimgray": Color(red=105, green=105, blue=105),
    "dodgerblue": Color(red=30, green=144, blue=255),
    "firebrick": Color(red=178, green=34, blue=34),
    "floralwhite": Color(red=255, green=250, blue=240),
    "forestgreen": Color(red=34, green=139, blue=34),
    "fuchsia": Color(red=255, green=0, blue=255),
    "gainsboro": Color(red=220, green=220, blue=220),
    "ghostwhite": Color(red=248, green=248, blue=255),
    "gold": Color(red=255, green=215, blue=0),
    "goldenrod": Color(red=218, green=165, blue=32),
    "gray": Color(red=127, green=127, blue=127),
    "green": Color(red=0, green=128, blue=0),
    "greenyellow": Color(red=173, green=255, blue=47),
    "honeydew": Color(red=240, green=255, blue=240),
    "hotpink": Color(red=255, green=105, blue=180),
    "indianred": Color(red=205, green=92, blue=92),
    "indigo": Color(red=75, green=0, blue=130),
    "ivory": Color(red=255, green=255, blue=240),
    "khaki": Color(red=240, green=230, blue=140),
    "lavender": Color(red=230, green=230, blue=250),
    "lavenderblush": Color(red=255, green=240, blue=245),
    "lawngreen": Color(red=124, green=252, blue=0),
    "lemonchiffon": Color(red=255, green=250, blue=205),
    "lightblue": Color(red=173, green=216, blue=230),
    "lightcoral": Color(red=240, green=128, blue=128),
    "lightcyan": Color(red=224, green=255, blue=255),
    "lightgoldenrodyellow": Color(red=250, green=250, blue=210),
    "lightgreen": Color(red=144, green=238, blue=144),
    "lightgrey": Color(red=211, green=211, blue=211),
    "lightpink": Color(red=255, green=182, blue=193),
    "lightsalmon": Color(red=255, green=160, blue=122),
    "lightseagreen": Color(red=32, green=178, blue=170),
    "lightskyblue": Color(red=135, green=206, blue=250),
    "lightslategray": Color(red=119, green=136, blue=153),
    "lightsteelblue": Color(red=176, green=196, blue=222),
    "lightyellow": Color(red=255, green=255, blue=224),
    "lime": Color(red=0, green=255, blue=0),
    "limegreen": Color(red=50, green=205, blue=50),
    "linen": Color(red=250, green=240, blue=230),
    "magenta": Color(red=255, green=0, blue=255),
    "maroon": Color(red=128, green=0, blue=0),
    "mediumaquamarine": Color(red=102, green=205, blue=170),
    "mediumblue": Color(red=0, green=0, blue=205),
    "mediumorchid": Color(red=186, green=85, blue=211),
    "mediumpurple": Color(red=147, green=112, blue=219),
    "mediumseagreen": Color(red=60, green=179, blue=113),
    "mediumslateblue": Color(red=123, green=104, blue=238),
    "mediumspringgreen": Color(red=0, green=250, blue=154),
    "mediumturquoise": Color(red=72, green=209, blue=204),
    "mediumvioletred": Color(red=199, green=21, blue=133),
    "midnightblue": Color(red=25, green=25, blue=112),
    "mintcream": Color(red=245, green=255, blue=250),
    "mistyrose": Color(red=255, green=228, blue=225),
    "moccasin": Color(red=255, green=228, blue=181),
    "navajowhite": Color(red=255, green=222, blue=173),
    "navy": Color(red=0, green=0, blue=128),
    "navyblue": Color(red=159, green=175, blue=223),
    "oldlace": Color(red=253, green=245, blue=230),
    "olive": Color(red=128, green=128, blue=0),
    "olivedrab": Color(red=107, green=142, blue=35),
    "orange": Color(red=255, green=165, blue=0),
    "orangered": Color(red=255, green=69, blue=0),
    "orchid": Color(red=218, green=112, blue=214),
    "palegoldenrod": Color(red=238, green=232, blue=170),
    "palegreen": Color(red=152, green=251, blue=152),
    "paleturquoise": Color(red=175, green=238, blue=238),
    "palevioletred": Color(red=219, green=112, blue=147),
    "papayawhip": Color(red=255, green=239, blue=213),
    "peachpuff": Color(red=255, green=218, blue=185),
    "peru": Color(red=205, green=133, blue=63),
    "pink": Color(red=255, green=192, blue=203),
    "plum": Color(red=221, green=160, blue=221),
    "powderblue": Color(red=176, green=224, blue=230),
    "purple": Color(red=128, green=0, blue=128),
    "red": Color(red=255, green=0, blue=0),
    "rosybrown": Color(red=188, green=143, blue=143),
    "royalblue": Color(red=65, green=105, blue=225),
    "saddlebrown": Color(red=139, green=69, blue=19),
    "salmon": Color(red=250, green=128, blue=114),
    "sandybrown": Color(red=250, green=128, blue=114),
    "seagreen": Color(red=46, green=139, blue=87),
    "seashell": Color(red=255, green=245, blue=238),
    "sienna": Color(red=160, green=82, blue=45),
    "silver": Color(red=192, green=192, blue=192),
    "skyblue": Color(red=135, green=206, blue=235),
    "slateblue": Color(red=106, green=90, blue=205),
    "slategray": Color(red=112, green=128, blue=144),
    "snow": Color(red=255, green=250, blue=250),
    "springgreen": Color(red=0, green=255, blue=127),
    "steelblue": Color(red=70, green=130, blue=180),
    "tan": Color(red=210, green=180, blue=140),
    "teal": Color(red=0, green=128, blue=128),
    "thistle": Color(red=216, green=191, blue=216),
    "tomato": Color(red=255, green=99, blue=71),
    "turquoise": Color(red=64, green=224, blue=208),
    "violet": Color(red=238, green=130, blue=238),
    "wheat": Color(red=245, green=222, blue=179),
    "white": Color(red=255, green=255, blue=255),
    "whitesmoke": Color(red=245, green=245, blue=245),
    "yellow": Color(red=255, green=255, blue=0),
    "yellowgreen": Color(red=154, green=205, blue=50),
}


def interpret_as_color(tokens: List[CSSToken]) -> Optional[Color]:
    """Attempts to interpret the given tokens as a color. This
    supports either a hexadecimal color (e.g., #333 or #333333) or
    one of the 140 named color values (
        https://www.w3.org/wiki/CSS/Properties/color/keywords
    )
    """
    if len(tokens) != 1:
        return None

    token = tokens[0]
    if token["type"] == CSSTokenType.ident:
        lowered_ident = token["value"].lower()
        return NAMED_CSS_COLORS.get(lowered_ident)

    if token["type"] == CSSTokenType.hash:
        val = token["value"]
        if len(val) != 3 and len(val) != 6:
            return None

        if not all(c in string.hexdigits for c in val):
            return None

        return Color.from_hex("#" + val)

    return None
