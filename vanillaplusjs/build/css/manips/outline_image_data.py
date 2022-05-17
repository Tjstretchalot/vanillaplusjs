from typing import Dict, List, Literal, Optional, Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.build.css.manipulator import CSSManipulator
from vanillaplusjs.build.css.token import CSSToken, CSSTokenType
import vanillaplusjs.build.handlers.hash as hash_handler
from urllib.parse import unquote, urlencode
import re
import os

from vanillaplusjs.constants import PROCESSOR_VERSION


IMAGE_DATA_REGEX = re.compile(
    r'^data:image/(?P<image_type>[^;,]+)[;,](?P<image_data>[^"]+)$'
)
"""Matches an image data source"""


class OutlineImageDataManipulator(CSSManipulator):
    """When encountering a url function whose value is an image data source,
    replaces it with a new url function which points to a file which contains
    the same data. Deduplicates within the file, but not across files.
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

        self.image_relpath_by_data: Optional[Dict[str, str]] = dict()
        self.image_counter = 0

        self.skip_next_url_function = False
        self.state: Optional[Literal["expecting_url", "expecting_string"]] = None
        self.stack: Optional[List[CSSToken]] = None

        path_in_gen = os.path.splitext(relpath)[0]
        if path_in_gen.startswith(os.path.join("src", "public")):
            path_in_gen = path_in_gen[
                len(os.path.join("src", "public")) + len(os.path.sep) :
            ]

        self.image_out_folder = os.path.join("out", "www", "img", "gen", path_in_gen)

    def start_mark(self, node: CSSToken) -> bool:
        if node["type"] != CSSTokenType.function:
            return False
        if node["value"] != "url":
            return False
        if self.skip_next_url_function:
            self.skip_next_url_function = False
            return False
        self.state = "expecting_url"
        self.stack = []
        return True

    def continue_mark(self, node: CSSToken) -> Optional[List[CSSToken]]:
        self.stack.append(node)

        if self.state == "expecting_url":
            assert (
                node["type"] == CSSTokenType.function
            ), "continue_mark in state expecting_url should get a function"
            assert (
                node["value"] == "url"
            ), "continue_mark in state expecting_url should get a url function"
            self.state = "expecting_string"
            return None

        assert (
            self.state == "expecting_string"
        ), f"continue_mark unknown state: {self.state=}"
        if node["type"] != CSSTokenType.string:
            self.skip_next_url_function = True
            result = self.stack
            self.stack = None
            self.state = None
            return result

        match = IMAGE_DATA_REGEX.match(node["value"])
        if match is None:
            self.skip_next_url_function = True
            result = self.stack
            self.stack = None
            self.state = None
            return result

        image_type = match.group("image_type")
        image_data = match.group("image_data")
        out_relpath = self.image_relpath_by_data.get(image_data)
        need_to_create = out_relpath is None
        if need_to_create:
            self.image_counter += 1
            file_ext = image_type.split("+", 1)[0]
            out_relpath = os.path.join(
                self.image_out_folder, f"{self.image_counter}.{file_ext}"
            )
            self.image_relpath_by_data[image_data] = out_relpath

        result: List[CSSToken] = [
            self.stack[0],
            CSSToken(
                type=CSSTokenType.string,
                value=out_relpath[len(os.path.join("out", "www")) :].replace(
                    os.path.sep, "/"
                ),
            ),
        ]
        self.stack = None
        self.state = None
        self.skip_next_url_function = True

        if self.mode == "scan":
            if need_to_create:
                self.produces.add(out_relpath)
                hash_scan_result = hash_handler.scan_file(self.context, out_relpath)
                self.dependencies.union(hash_scan_result.dependencies)
                self.produces.union(hash_scan_result.produces)
            return result

        out_path = os.path.join(self.context.folder, out_relpath)
        if need_to_create:
            if os.path.lexists(out_relpath):
                self.reused.add(out_relpath)
            else:
                self.produced.add(out_relpath)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", newline="\n") as f:
                    f.write(unquote(image_data))

            hash_build_result = hash_handler.build_file(self.context, out_relpath)
            self.children.union(hash_build_result.children)
            self.produced.union(hash_build_result.produced)
            self.reused.union(hash_build_result.reused)

        with open(out_path + ".hash") as f:
            hash_value = f.read()

        result[1]["value"] += "?" + urlencode(
            {"v": hash_value, "pv": PROCESSOR_VERSION}
        )

        return result

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
