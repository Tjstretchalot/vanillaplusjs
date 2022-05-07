from typing import List, Literal, Optional, Set
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.scan_file import ScanFileResult
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)
PROCESSOR_VERSION = "1"


with open(
    os.path.abspath(os.path.join(__file__, "../../../../../setup.cfg")), "r"
) as f:
    for line in f:
        line: str
        if line.startswith("version = "):
            PROCESSOR_VERSION = line.split("=")[1].strip()


class LinkRelStylesheetHash(HTMLManipulator):
    """Updates stylesheet links which reference domain-relative links (i.e., like
    /css/main.css) to append the hash of the file and the current processor version

    For example,

    ```
    <link rel="stylesheet" href="/css/main.css">
    ```

    would become

    ```
    <link rel="stylesheet" href="/css/main.css?v=HASH&pv=PROCESSOR_VERSION>
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

        dep_with_os_sep = dep.replace("/", os.path.sep)
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
        dep_with_os_sep = dep.replace("/", os.path.sep)
        rel_to_out = os.path.join("out", "www", dep_with_os_sep)

        expected_hash_loc = os.path.join(self.context.folder, rel_to_out + ".hash")
        assert os.path.exists(expected_hash_loc), expected_hash_loc + " should exist"

        with open(expected_hash_loc, "r") as f:
            hash = f.read().strip()

        return [
            tkn.HTMLToken(
                type="EmptyTag",
                name="link",
                data={
                    (None, "rel"): "stylesheet",
                    (None, "href"): f"/{dep}?v={hash}&pv={PROCESSOR_VERSION}",
                },
            )
        ]

    def _get_as_dependency(self, node: tkn.HTMLToken) -> Optional[str]:
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
        if rel != "stylesheet":
            return None

        href = attributes.get((None, "href"))
        print(f"{node=}")
        if href is None or not href.startswith("/") or any(c in "?#" for c in href):
            return None

        return href[1:]

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=list(self.dependencies), produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=list(self.children), produced=[], reused=[])
