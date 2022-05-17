from typing import Dict, List, Literal, Optional, Set
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
import os
from vanillaplusjs.constants import PROCESSOR_VERSION
from dataclasses import dataclass
from urllib.parse import urlencode
import itertools
import abc


PUBLIC_PREFIX_LENGTH = len(os.path.join("src", "public")) + len(os.path.sep)


@dataclass
class LinkDependency:
    """Used to describe a link dependency that we are going to
    append the cache-busting query parameters to
    """

    name: str
    """The name of the tag"""

    attr_name: str
    """The name of the attribute that refers to the file to link to."""

    path: str
    """The path that we originally wanted to link to."""

    attributes: Dict[str, str]
    """The other attributes besides `name`"""


class LinkLike(abc.ABC):
    """Base class for describing something that we should append cache-busting
    query parameters to.
    """

    def __init__(
        self, tag_style: Literal["EmptyTag", "StartTag"], name: str, attr_name: str
    ) -> None:
        self.tag_style = tag_style
        self.name = name
        self.attr_name = attr_name

    @abc.abstractmethod
    def matches(self, node: tkn.HTMLToken) -> bool:
        """Returns True if the given node is a link of the type we are looking for.
        This can ignore the name and attribute name.
        """
        raise NotImplementedError()


class LinkBasic(LinkLike):
    def matches(self, node: tkn.HTMLToken) -> bool:
        return True


class LinkRel(LinkLike):
    def __init__(self) -> None:
        super().__init__("EmptyTag", "link", "href")

    def matches(self, node: tkn.HTMLToken) -> bool:
        return node["data"].get((None, "rel")) in ("stylesheet", "preload")


LINK_TYPES = (
    LinkRel(),
    LinkBasic("StartTag", "script", "src"),
)


class LinkHash(HTMLManipulator):
    """Updates a variety of whats of referencing other files such that they
    reference the same file with query parameters which include the version of
    the file they reference. This allows the server to offer strong cache-control
    headers, while still ensuring that clients will always get the latest version

    Examples:

    ```
    <link as="font" href="/assets/fonts/test.ttf" rel="preload" type="font/ttf">
    ```

    would become

    ```
    <link as="font" href="/assets/fonts/test.ttf?v=HASH&pv=PROCESSOR_VERSION" rel="preload" type="font/ttf">
    ```

    and

    ```
    <link rel="stylesheet" href="/css/main.css">
    ```

    would become

    ```
    <link rel="stylesheet" href="/css/main.css?v=HASH&pv=PROCESSOR_VERSION>
    ```

    For convenience when testing, this will always alphabetically organize
    the attributes.
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

        new_attribute_keys = sorted(
            itertools.chain(dep.attributes.keys(), (dep.attr_name,))
        )
        new_href = f"/{dep.path}?" + urlencode({"v": hash, "pv": PROCESSOR_VERSION})

        new_data = dict(
            ((None, key), dep.attributes[key])
            if key != dep.attr_name
            else ((None, key), new_href)
            for key in new_attribute_keys
        )

        return [
            tkn.HTMLToken(
                type=node["type"],
                name=dep.name,
                data=new_data,
            )
        ]

    def _get_as_dependency(self, node: tkn.HTMLToken) -> Optional[LinkDependency]:
        """If the given node is a proper link to a stylesheet that we should update,
        returns the path to the stylesheet relative to the public directory.

        Otherwise, returns None.
        """
        for link_type in LINK_TYPES:
            if node["type"] != link_type.tag_style:
                continue

            if node["name"] != link_type.name:
                continue

            if not link_type.matches(node):
                continue
            break
        else:
            return None

        attributes = node["data"]
        href = attributes.get((None, link_type.attr_name))
        if href is None or not href.startswith("/") or any(c in "?#" for c in href):
            return None

        return LinkDependency(
            name=node["name"],
            attr_name=link_type.attr_name,
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
