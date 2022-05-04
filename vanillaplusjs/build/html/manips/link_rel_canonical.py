from typing import List, Literal, Optional
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.exceptions import MissingConfigurationException
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os

from vanillaplusjs.build.scan_file import ScanFileResult


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)


class LinkRelCanonicalManipulator(HTMLManipulator):
    """Converts canonical url hints which either do not specify their href
    or use a relative url for their href into absolute urls.

    For example,

    ```
    <link rel="canonical">
    ```

    becomes

    ```
    <link href="https://example.com/index.html" rel="canonical">
    ```
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        if node["type"] != "EmptyTag":
            return False

        if node["name"] != "link":
            return False

        attributes = node["data"]
        if (None, "rel") not in attributes:
            return False

        rel = attributes[(None, "rel")]
        if rel != "canonical":
            return False

        href = attributes.get((None, "href"))
        if href is not None and href != "" and not href.startswith("/"):
            return False

        if self.mode == "scan":
            if self.context.host is None:
                raise MissingConfigurationException(
                    f'host must be set in order to update canonical links in "{self.relpath}"'
                )
            return False

        return True

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        host = self.context.host
        href = node["data"].get((None, "href"))

        new_href = None
        if href is None:
            path_relative_to_public = self.relpath[PUBLIC_PREFIX_LENGTH:]
            path = path_relative_to_public.replace(os.path.sep, "/")
            new_href = f"https://{host}/{path}"
        else:
            new_href = f"https://{host}{href}"

        new_node = tkn.empty_tag("link", {"href": new_href, "rel": "canonical"})
        return [new_node]

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=[], produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=[], produced=[], reused=[])
