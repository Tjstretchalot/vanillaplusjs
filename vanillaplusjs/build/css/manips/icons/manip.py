from vanillaplusjs.build.css.manips.icons.command import IconCommand
from vanillaplusjs.build.css.manips.icons.parser import parse_icon_command
from vanillaplusjs.build.css.manips.icons.settings import ButtonSetting
from vanillaplusjs.build.css.manips.icons.tokenizer import tokenize
from vanillaplusjs.build.css.manipulator import CSSManipulator
from typing import List, Literal, Optional, Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.build.css.token import CSSToken, CSSTokenType
from loguru import logger
import re
import os
import dataclasses
import io


PREPROCESSOR_ICON_ACTION_RULE = re.compile(
    r"^\s*!\s*PREPROCESSOR\s*:\s+icon\s+(?P<args>.*)\s*$", flags=re.DOTALL
)
"""
Regex that matches !PREPROCESSOR: icon [args]
allows newlines in args
"""


class IconManipulator(CSSManipulator):
    """Allows for easily introducing icons into the project, generating the
    necessary boilerplate from a single configurable command.

    Suppose you have a simple circle icon, which is defined as an SVG and
    has a single color, which exactly matches your `primary` color. This
    will handle converting that SVG into all your standard colors and icon
    sizes, as well as generate a button class (or button classes if desired).

    This expects your UI kit to be defined in your `main.css` file
    using CSS variables. In particular, css variables starting with `col-`
    define the colors, and css variables starting with `icon-size-` define
    the icon sizes.
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode

        self.dependencies: Optional[Set[str]] = set() if mode == "scan" else None
        self.produces: Optional[Set[str]] = set() if mode == "scan" else None

        self.children: Optional[Set[str]] = set() if mode == "build" else None
        self.produced: Optional[Set[str]] = set() if mode == "build" else None
        self.reused: Optional[Set[str]] = set() if mode == "build" else None

    def start_mark(self, node: CSSToken) -> bool:
        """Returns True if we would like to start a replacement mark at the given
        node, false otherwise.
        """
        args = self.get_icon_command_args(node)
        if args is None:
            return False
        if self.mode == "scan":
            self.scan_icon_command(args)
            return False
        return True

    def continue_mark(self, node: CSSToken) -> Optional[List[CSSToken]]:
        args = self.get_icon_command_args(node)
        assert args is not None, "continue_mark on non-icon command"

        svg = None
        replacer = None

        for color in args.output_colors:
            output_relpath = os.path.join(args.output_icon_folder, color + ".svg")
            output_path = os.path.join(self.context.folder, output_relpath)
            if os.path.exists(output_path):
                self.reused.add(output_relpath)
                continue
            if svg is None:
                with open(os.path.join(self.context.folder, args.input_icon)) as f:
                    svg = f.read()

                og_color = self.context.icon_settings.color_map[args.icon_initial_color]
                replacer = f'"{og_color.to_hex()}"'
                if replacer not in svg:
                    logger.warning(
                        f"Icon {args.icon_name} does not have the "
                        f"color {args.icon_initial_color} ({og_color.to_hex()}) in it"
                    )
                    logger.debug(f"{svg=}")
                    logger.debug(f"{replacer=}")

            target_color = self.context.icon_settings.color_map[color]
            new_svg = svg.replace(replacer, f'"{target_color.to_hex()}"')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(new_svg)
            self.produced.add(output_relpath)

        resulting_tokens = []
        for size in args.output_sizes:
            for color in args.output_colors:
                if resulting_tokens:
                    resulting_tokens.append(
                        CSSToken(type=CSSTokenType.whitespace, value="\n\n")
                    )
                resulting_tokens.extend(
                    [
                        CSSToken(type=CSSTokenType.delim, value="."),
                        CSSToken(
                            type=CSSTokenType.ident,
                            value=f"icon-{args.icon_name}-{size}-{color}",
                        ),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.left_curly_bracket),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="background"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.ident, value="no-repeat"),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.ident, value="center"),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.ident, value="center"),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="display"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.ident, value="inline-block"),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="vertical-align"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.ident, value="middle"),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="content"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.string, value=""),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="width"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.function, value="var"),
                        CSSToken(type=CSSTokenType.ident, value=f"--icon-size-{size}"),
                        CSSToken(type=CSSTokenType.right_parens),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="height"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.function, value="var"),
                        CSSToken(type=CSSTokenType.ident, value=f"--icon-size-{size}"),
                        CSSToken(type=CSSTokenType.right_parens),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="background-size"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.percentage, value="100"),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.percentage, value="100"),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                        CSSToken(type=CSSTokenType.ident, value="background-image"),
                        CSSToken(type=CSSTokenType.colon),
                        CSSToken(type=CSSTokenType.whitespace, value=" "),
                        CSSToken(type=CSSTokenType.function, value="url"),
                        CSSToken(
                            type=CSSTokenType.string, value=args.web_path_to(color)
                        ),
                        CSSToken(type=CSSTokenType.right_parens),
                        CSSToken(type=CSSTokenType.semicolon),
                        CSSToken(type=CSSTokenType.whitespace, value="\n"),
                        CSSToken(type=CSSTokenType.right_curly_bracket),
                    ]
                )

        def append_btn(size: str, suffix: str, settings: ButtonSetting):
            """
            .icon-btn-{args.icon_name}-{size}{suffix} {
                -webkit-appearance: none;
                appearance: none;
                background: transparent;
                border: none;
                border-radius: 0;
                box-shadow: none;
                outline: none;
                padding: 0;
                margin: 0;
                text-align: center;
                display: inline-block;
                cursor: pointer;
            }

            .icon-btn-{args.icon_name}-{size}{suffix}:disabled {
                cursor: not-allowed;
            }

            .icon-btn-{args.icon_name}-{size}{suffix} .icon-btn--icon {
                background: no-repeat center center;
                display: inline-block;
                vertical-align: middle;
                content: '';
                width: var(--icon-size-medium);
                height: var(--icon-size-medium);
                background-size: 100% 100%;
                background-image: url("{args.web_path_to(settings.active_color)}");
            }

            .icon-btn-{args.icon_name}-{size}{suffix}:hover .icon-btn--icon {
                background-image: url("{args.web_path_to(settings.hover_color)}");
            }

            .icon-btn-{args.icon_name}-{size}{suffix}:disabled .icon-btn--icon {
                background-image: url("{args.web_path_to(settings.disabled_color)}");
            }
            """
            resulting_tokens.extend(
                [
                    CSSToken(type=CSSTokenType.whitespace, value="\n\n"),
                    CSSToken(type=CSSTokenType.delim, value="."),
                    CSSToken(
                        type=CSSTokenType.ident,
                        value=f"icon-btn-{args.icon_name}-{size}{suffix}",
                    ),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.left_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="-webkit-appearance"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="none"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="appearance"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="none"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="transparent"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="border"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="none"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="border-radius"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="0"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="box-shadow"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="none"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="outline"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="none"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="padding"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="0"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="margin"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="0"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="text-align"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="center"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="display"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="inline-block"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="cursor"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="pointer"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n"),
                    CSSToken(type=CSSTokenType.right_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n\n"),
                    CSSToken(type=CSSTokenType.delim, value="."),
                    CSSToken(
                        type=CSSTokenType.ident,
                        value=f"icon-btn-{args.icon_name}-{size}{suffix}:disabled",
                    ),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.left_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="cursor"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="not-allowed"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n"),
                    CSSToken(type=CSSTokenType.right_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n\n"),
                    CSSToken(type=CSSTokenType.delim, value="."),
                    CSSToken(
                        type=CSSTokenType.ident,
                        value=f"icon-btn-{args.icon_name}-{size}{suffix} .icon-btn--icon",
                    ),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.left_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="no-repeat"),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="center"),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="center"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="display"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="inline-block"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="vertical-align"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.ident, value="middle"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="content"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.string, value=""),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="width"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.function, value="var"),
                    CSSToken(type=CSSTokenType.ident, value=f"--icon-size-{size}"),
                    CSSToken(type=CSSTokenType.right_parens),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="height"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.function, value="var"),
                    CSSToken(type=CSSTokenType.ident, value=f"--icon-size-{size}"),
                    CSSToken(type=CSSTokenType.right_parens),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background-size"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.percentage, value="100"),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.percentage, value="100"),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background-image"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.function, value="url"),
                    CSSToken(
                        type=CSSTokenType.string,
                        value=args.web_path_to(settings.active_color),
                    ),
                    CSSToken(type=CSSTokenType.right_parens),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n"),
                    CSSToken(type=CSSTokenType.right_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n\n"),
                    CSSToken(type=CSSTokenType.delim, value="."),
                    CSSToken(
                        type=CSSTokenType.ident,
                        value=f"icon-btn-{args.icon_name}-{size}{suffix}:hover .icon-btn--icon",
                    ),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.left_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background-image"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.function, value="url"),
                    CSSToken(
                        type=CSSTokenType.string,
                        value=args.web_path_to(settings.hover_color),
                    ),
                    CSSToken(type=CSSTokenType.right_parens),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n"),
                    CSSToken(type=CSSTokenType.right_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n\n"),
                    CSSToken(type=CSSTokenType.delim, value="."),
                    CSSToken(
                        type=CSSTokenType.ident,
                        value=f"icon-btn-{args.icon_name}-{size}{suffix}:disabled .icon-btn--icon",
                    ),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.left_curly_bracket),
                    CSSToken(type=CSSTokenType.whitespace, value="\n    "),
                    CSSToken(type=CSSTokenType.ident, value="background-image"),
                    CSSToken(type=CSSTokenType.colon),
                    CSSToken(type=CSSTokenType.whitespace, value=" "),
                    CSSToken(type=CSSTokenType.function, value="url"),
                    CSSToken(
                        type=CSSTokenType.string,
                        value=args.web_path_to(settings.disabled_color),
                    ),
                    CSSToken(type=CSSTokenType.right_parens),
                    CSSToken(type=CSSTokenType.semicolon),
                    CSSToken(type=CSSTokenType.whitespace, value="\n"),
                    CSSToken(type=CSSTokenType.right_curly_bracket),
                ]
            )

        if args.button is not None:
            for size in args.output_sizes:
                if args.button.default_button is not None:
                    append_btn(size, "", args.button.default_button)

                for iden, setting in args.button.button_by_identifier.items():
                    append_btn(size, f"-{iden}", setting)

        return resulting_tokens

    def get_icon_command_args(self, node: CSSToken) -> Optional[IconCommand]:
        if node["type"] != CSSTokenType.comment:
            return None

        match = PREPROCESSOR_ICON_ACTION_RULE.match(node["value"])
        if match is None:
            return None

        args_str = match.group("args")
        tokens = tokenize(io.StringIO(args_str))
        parser = parse_icon_command()
        next(parser)

        try:
            for token in tokens:
                parser.send(token)
            return None
        except StopIteration as e:
            args: IconCommand = e.value

        if args.icon_initial_color not in self.context.icon_settings.color_map:
            return

        real_colors = (
            list(
                dict(  # dict to preserve order
                    (color, None)
                    for color in args.output_colors
                    if color in self.context.icon_settings.color_map
                )
            )
            if args.output_colors is not None
            else self.context.icon_settings.color_map.keys()
        )
        real_sizes = (
            list(
                dict(  # dict to preserve order
                    (size, None)
                    for size in args.output_sizes
                    if size in self.context.icon_settings.sizes
                )
            )
            if args.output_sizes is not None
            else self.context.icon_settings.sizes
        )

        if not real_colors or not real_sizes:
            return None

        real_button = (
            args.button
            if args.button != "default"
            else self.context.icon_settings.default_button
        )

        if real_button is not None:

            def is_setting_bad(setting: ButtonSetting) -> bool:
                return (
                    setting.active_color not in self.context.icon_settings.color_map
                    or setting.hover_color not in self.context.icon_settings.color_map
                    or setting.disabled_color
                    not in self.context.icon_settings.color_map
                )

            if real_button.default_button is not None and is_setting_bad(
                real_button.default_button
            ):
                real_button = dataclasses.replace(real_button, default_button=None)

            purge_idens = set()
            for iden, setting in real_button.button_by_identifier.items():
                if is_setting_bad(setting):
                    purge_idens.add(iden)

            if purge_idens:
                real_button = dataclasses.replace(
                    real_button,
                    button_by_identifier=dict(
                        (iden, setting)
                        for iden, setting in real_button.button_by_identifier
                        if iden not in purge_idens
                    ),
                )

        return dataclasses.replace(
            args, output_colors=real_colors, output_sizes=real_sizes, button=real_button
        )

    def scan_icon_command(self, args: IconCommand) -> None:
        """Adds any dependencies or produces appropriate for the icon command
        with the given arguments.
        """
        self.dependencies.add(args.input_icon)

        for color in args.output_colors:
            self.produces.add(os.path.join(args.output_icon_folder, color + ".svg"))

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator"""
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator."""
        return BuildFileResult(
            children=list(self.children),
            produced=list(self.produced),
            reused=list(self.reused),
        )
