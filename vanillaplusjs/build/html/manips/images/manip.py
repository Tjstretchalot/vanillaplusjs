from typing import List, Literal, Optional, Set
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os
import re
from vanillaplusjs.build.html.manips.images.command import (
    ImageCommand,
    parse_command,
    validate_command,
)
from vanillaplusjs.build.html.manips.images.exporter import export_command
from vanillaplusjs.build.html.manips.images.scanner import scan_command


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)


PREPROCESSOR_IMAGE_ACTION_RULE = re.compile(r"^\s*\[\s*IMAGE\s*:\s+(?P<args>.*)\]\s*$")
"""
Regex that matches [IMAGE: <args>]
"""


class ImagesManipulator(HTMLManipulator):
    """ """

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

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        cmd = self._get_command(node)
        if cmd is None:
            return False

        if self.mode == "scan":
            scan_result = scan_command(
                self.context, os.path.join(self.context.folder, self.relpath), cmd
            )
            self.dependencies.update(scan_result.dependencies)
            self.produces.update(scan_result.produces)
            return False

        return True

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        cmd = self._get_command(node)
        assert cmd is not None, "continue mark without command"
        command_file_path = os.path.join(self.context.folder, self.relpath)
        metadata, build_result = export_command(self.context, command_file_path, cmd)
        self.children.update(build_result.children)
        self.produced.update(build_result.produced)
        self.reused.update(build_result.reused)

        res: List[tkn.HTMLToken] = [
            tkn.HTMLToken(type="StartTag", name="picture", data=dict())
        ]

        for format_name, outputs in metadata.target.outputs.items():
            if format_name == self.context.image_settings.default_format:
                continue

            res.append(
                tkn.HTMLToken(
                    type="EmptyTag",
                    name="source",
                    data={
                        (None, "srcset"): ", ".join(
                            f"/{output.relpath.replace(os.path.sep, '/')} {output.width}w"
                            for output in outputs
                        )
                    },
                )
            )

        default_outputs = metadata.target.outputs[
            self.context.image_settings.default_format
        ]
        standard_resolution_output = next(
            output
            for output in default_outputs
            if output.width == cmd.width and output.height == cmd.height
        )
        res.append(
            tkn.HTMLToken(
                type="EmptyTag",
                name="img",
                data={
                    (None, "width"): str(cmd.width),
                    (None, "height"): str(cmd.height),
                    (None, "src"): "/"
                    + standard_resolution_output.relpath.replace(os.path.sep, "/"),
                    (None, "srcset"): ", ".join(
                        f"/{output.relpath.replace(os.path.sep, '/')} {output.width}w"
                        for output in default_outputs
                    ),
                    **({(None, "loading"): "lazy"} if cmd.lazy else dict()),
                },
            )
        )
        res.append(tkn.HTMLToken(type="EndTag", name="picture"))
        return res

    def _get_command(self, node: tkn.HTMLToken) -> Optional[ImageCommand]:
        """If the given node corresponds to a preprocessor command to insert
        an image, returns the command. Otherwise, returns None
        """
        if node["type"] != "Comment":
            return None
        match = PREPROCESSOR_IMAGE_ACTION_RULE.match(node["data"])
        if not match:
            return None

        args = match.group("args")
        cmd = parse_command(args)
        if cmd is None:
            return None

        if not validate_command(
            cmd, self.context, os.path.join(self.context.folder, self.relpath)
        ):
            return None

        return cmd

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(
            children=list(self.children),
            produced=list(self.produced),
            reused=list(self.reused),
        )
