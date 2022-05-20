from typing import Dict, List, Literal, Optional
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.exceptions import MissingConfigurationException
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os
from dataclasses import dataclass
from vanillaplusjs.build.scan_file_result import ScanFileResult


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)


@dataclass
class TagToReplace:
    """Describes a tag with an attribute which functions like the href in a
    link rel canonical tag.
    """

    name: str
    """The name of the tag"""

    attr: str
    """The name of the attribute which functions like href"""

    other_tags: Dict[str, str]
    """A dictionary of other tags which should be included in the tag"""


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

    This functions identically for meta tags with property="og:url"
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        tag = self.try_get_tag(node)
        if tag is None:
            return

        if self.mode == "scan":
            if self.context.host is None:
                raise MissingConfigurationException(
                    f'host must be set in order to update canonical links in "{self.relpath}"'
                )
            return False

        return True

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        host = self.context.host
        tag = self.try_get_tag(node)

        href = node["data"].get((None, tag.attr))
        new_href = None
        if href is None:
            path_relative_to_public = self.relpath[PUBLIC_PREFIX_LENGTH:]
            path = path_relative_to_public.replace(os.path.sep, "/")
            new_href = f"https://{host}/{path}"
        else:
            new_href = f"https://{host}{href}"

        new_tags = tag.other_tags.copy()
        new_tags[tag.attr] = new_href
        new_tags = dict((k, new_tags[k]) for k in sorted(new_tags.keys()))
        new_node = tkn.empty_tag(tag.name, new_tags)
        return [new_node]

    def try_get_tag(self, node: tkn.HTMLToken) -> Optional[TagToReplace]:
        tag = self.try_get_tag_inner(node)
        if tag is None:
            return None

        href = node["data"].get((None, tag.attr))
        if href is not None and href.startswith("http"):
            return None

        tag.other_tags = dict(
            (key, value) for (_, key), value in node["data"].items() if key != tag.attr
        )
        return tag

    def try_get_tag_inner(self, node: tkn.HTMLToken) -> Optional[TagToReplace]:
        if node["type"] != "EmptyTag":
            return None

        if node["name"] == "link":
            rel = node["data"].get((None, "rel"))
            if rel == "canonical":
                return TagToReplace(
                    name="link",
                    attr="href",
                    other_tags=None,
                )
            return None

        if node["name"] == "meta":
            property = node["data"].get((None, "property"))
            if property == "og:url":
                return TagToReplace(
                    name="meta",
                    attr="content",
                    other_tags=None,
                )
            return None

        return None

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=[], produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=[], produced=[], reused=[])
