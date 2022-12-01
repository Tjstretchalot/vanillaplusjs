from typing import List, Literal, Optional, Set
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.css.manipulator import CSSManipulator
from vanillaplusjs.build.css.token import CSSToken, CSSTokenType
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.scan_file_result import ScanFileResult
from dataclasses import dataclass
from urllib.parse import urlencode
import os

from vanillaplusjs.constants import PROCESSOR_VERSION


@dataclass
class VersionSuffix:
    path_from_public: str
    """The path to the file, relative to the public folder"""

    path_from_root: str
    """The path to the file, relative to the project root"""


class VersionURLsManipulator(CSSManipulator):
    """When encountering a url() function, replaces it with a new url() function
    which includes a query string with the file's hash and the current processor
    version. This ensures the file is redownloaded when it may have changed.
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
        self.produced: Optional[List[str]] = [] if mode == "build" else None
        self.reused: Optional[List[str]] = [] if mode == "build" else None

        self._in_url = False

    def start_mark(self, node: CSSToken) -> bool:
        if self._in_url:
            if node["type"] == CSSTokenType.right_parens:
                self._in_url = False
                return False

            if node["type"] == CSSTokenType.string:
                new_suffix = self._decide_new_version_suffix(node["value"])
                if new_suffix is not None:
                    if self.mode == "scan":
                        self.dependencies.add(new_suffix.path_from_root)
                        return False
                    return True

            return False

        if node["type"] == CSSTokenType.url:
            # unquoted url token
            new_suffix = self._decide_new_version_suffix(node["value"])
            if new_suffix is not None:
                if self.mode == "scan":
                    self.dependencies.add(new_suffix.path_from_root)
                    return False
                return True
            return False

        if node["type"] == CSSTokenType.function and node["value"].lower() == "url":
            self._in_url = True
            return False

        return False

    def _decide_new_version_suffix(self, url: str) -> Optional[VersionSuffix]:
        if not url.startswith("/"):
            return None

        if "?" in url:
            return None

        path_relative_to_public = url[1:].replace("/", os.path.sep)
        path_relative_to_root = os.path.join("src", "public", path_relative_to_public)

        if path_relative_to_root == self.relpath:
            return None

        return VersionSuffix(
            path_from_public=path_relative_to_public,
            path_from_root=path_relative_to_root,
        )

    def continue_mark(self, node: CSSToken) -> Optional[List[CSSToken]]:
        new_suffix = self._decide_new_version_suffix(node["value"])
        if new_suffix is None:
            return [node]

        with open(
            os.path.join(
                self.context.out_folder, "www", new_suffix.path_from_public + ".hash"
            )
        ) as f:
            hash_value = f.read()

        suffix_to_add = "?" + urlencode({"v": hash_value, "pv": PROCESSOR_VERSION})
        new_value = node["value"] + suffix_to_add

        cp_node = node.copy()
        cp_node["value"] = new_value
        return [cp_node]

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator"""
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator."""
        return BuildFileResult(
            children=list(self.children), produced=self.produced, reused=self.reused
        )
