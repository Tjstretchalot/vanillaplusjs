from typing import Dict, List, Literal, Optional, Set
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.scan_file import ScanFileResult
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os
from vanillaplusjs.constants import PROCESSOR_VERSION
from dataclasses import dataclass
import itertools


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)


@dataclass
class PreloadDependency:
    path: str
    attributes: Dict[str, str]


class LinkRelPreloadHash(HTMLManipulator):
    """Updates preload links which reference domain-relative links (i.e., like
    /css/main.css) to append the hash of the file and the current processor version

    For example,

    ```
    <link as="font" href="/assets/fonts/test.ttf" rel="preload" type="font/ttf">
    ```

    would become

    ```
    <link as="font" href="/assets/fonts/test.ttf?v=HASH&pv=PROCESSOR_VERSION" rel="preload" type="font/ttf">
    ```
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode

        self.dependencies: Optional[Set[str]] = set() if mode == "scan" else None
        self.children: Optional[Set[str]] = set() if mode == "build" else None

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        dep = self._get_as_dependency(node)
        if dep is None:
            return False

        dep_with_os_sep = dep.path.replace("/", os.path.sep)
        rel_to_public = os.path.join("src", "public", dep_with_os_sep)

        if self.mode == "scan":
            self.dependencies.add(rel_to_public)
            return False

        self.children.add(rel_to_public)
        return True

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        """Updates the given node to include the hash of the stylesheet file
        and the processor version.
        """
        dep = self._get_as_dependency(node)
        dep_with_os_sep = dep.path.replace("/", os.path.sep)
        rel_to_out = os.path.join("out", "www", dep_with_os_sep)

        expected_hash_loc = os.path.join(self.context.folder, rel_to_out + ".hash")
        assert os.path.exists(expected_hash_loc), expected_hash_loc + " should exist"

        with open(expected_hash_loc, "r") as f:
            hash = f.read().strip()

        new_attribute_keys = sorted(itertools.chain(dep.attributes.keys(), ("href",)))
        new_href = f"/{dep.path}?v={hash}&pv={PROCESSOR_VERSION}"

        return [
            tkn.HTMLToken(
                type="EmptyTag",
                name="link",
                data=dict(
                    ((None, key), dep.attributes[key])
                    if key != "href"
                    else ((None, key), new_href)
                    for key in new_attribute_keys
                ),
            )
        ]

    def _get_as_dependency(self, node: tkn.HTMLToken) -> Optional[PreloadDependency]:
        """If the given node is a proper link to a stylesheet that we should update,
        returns the path to the stylesheet relative to the public directory.

        Otherwise, returns None.
        """
        if node["type"] != "EmptyTag":
            return None

        if node["name"] != "link":
            return None

        attributes = node["data"]
        if (None, "rel") not in attributes:
            return None

        rel = attributes[(None, "rel")]
        if rel != "preload":
            return None

        href = attributes.get((None, "href"))
        if href is None or not href.startswith("/") or any(c in "?#" for c in href):
            return None

        return PreloadDependency(
            path=href[1:],
            attributes=dict(
                ((key[1], val) for (key, val) in attributes.items() if key[1] != "href")
            ),
        )

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=list(self.dependencies), produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=list(self.children), produced=[], reused=[])
