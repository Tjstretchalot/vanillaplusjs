import errno
from typing import Dict, List, Literal, Optional, Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.html.manipulator import HTMLManipulator
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.handlers.handler import Handler
import os
import io
from urllib.parse import urlencode
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.constants import PROCESSOR_VERSION


class OutlineManipulator(HTMLManipulator):
    """Upon encountering a script tag without a src or a style
    tag, this will add a new script tag with the src pointing to the generated
    file, or a link tag with the href pointing to the generated file,
    respectively.

    The newly generated file will go through standard javascript and
    css processing.
    """

    def __init__(
        self,
        context: BuildContext,
        relpath: str,
        mode: Literal["scan", "build"],
        js_handler: Handler,
        css_handler: Handler,
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode
        self.js_handler = js_handler
        self.css_handler = css_handler

        self.dependencies: Optional[Set[str]] = set() if mode == "scan" else None
        self.produces: Optional[Set[str]] = set() if mode == "scan" else None

        self.children: Optional[Set[str]] = set() if mode == "build" else None
        self.produced: Optional[Set[str]] = set() if mode == "build" else None
        self.reused: Optional[Set[str]] = set() if mode == "build" else None

        self.script_outline_count = 0
        self.style_outline_count = 0

        path_in_gen = os.path.splitext(relpath)[0]
        if path_in_gen.startswith(os.path.join("src", "public")):
            path_in_gen = path_in_gen[
                len(os.path.join("src", "public")) + len(os.path.sep) :
            ]

        self.script_src_folder = os.path.join("src", "public", "js", "gen", path_in_gen)

        self.script_out_folder = os.path.join("out", "www", "js", "gen", path_in_gen)

        self.style_src_folder = os.path.join("src", "public", "css", "gen", path_in_gen)

        self.style_out_folder = os.path.join("out", "www", "css", "gen", path_in_gen)

        self.outlining: Optional[Literal["script", "style"]] = None
        self.outlining_to_path: Optional[str] = None
        """Relative to project root"""
        self.outlining_to: Optional[io.TextIOBase] = None
        self.start_tag_attrs: Optional[Dict[str, str]] = None
        """The attributes to preserve on the start tag"""

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        # We need to actually outline even in scan mode, since we need
        # to scan the contents of the fake "src" file in order to determine
        # dependencies.
        return self._should_outline_script(node) or self._should_outline_style(node)

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        if self.outlining is None:
            if self._should_outline_script(node):
                self.outlining = "script"
                if self.script_outline_count == 0:
                    os.makedirs(
                        os.path.join(self.context.folder, self.script_src_folder),
                        exist_ok=True,
                    )
                self.script_outline_count += 1
                self.outlining_to_path = os.path.join(
                    self.script_src_folder,
                    f"{self.script_outline_count}.js",
                )
                self.outlining_to = open(
                    os.path.join(self.context.folder, self.outlining_to_path), "w"
                )
                self.start_tag_attrs = dict(
                    (key, val) for (_, key), val in node["data"].items()
                )
                return None
            if self._should_outline_style(node):
                self.outlining = "style"
                if self.style_outline_count == 0:
                    os.makedirs(
                        os.path.join(self.context.folder, self.style_src_folder),
                        exist_ok=True,
                    )
                self.style_outline_count += 1
                self.outlining_to_path = os.path.join(
                    self.style_src_folder,
                    f"{self.style_outline_count}.css",
                )
                self.outlining_to = open(
                    os.path.join(self.context.folder, self.outlining_to_path), "w"
                )
                self.start_tag_attrs = dict(
                    (key, val) for (_, key), val in node["data"]
                )
                return None

            raise ValueError(f"Unexpected tag {node}")

        if node["type"] == "EndTag":
            self.outlining_to.close()
            self.outlining_to = None

            handler = (
                self.js_handler if self.outlining == "script" else self.css_handler
            )
            if self.mode == "scan":
                scan_result = handler.scan_file(self.context, self.outlining_to_path)
                self.dependencies.update(scan_result.dependencies)
                self.produces.update(scan_result.produces)
            else:
                build_result = handler.build_file(self.context, self.outlining_to_path)
                self.children.update(build_result.children)
                self.produced.update(build_result.produced)
                self.reused.update(build_result.reused)

            os.remove(os.path.join(self.context.folder, self.outlining_to_path))
            possibly_empty_folder: str = os.path.dirname(self.outlining_to_path)

            while possibly_empty_folder.count(os.path.sep) > 2:
                try:
                    os.rmdir(os.path.join(self.context.folder, possibly_empty_folder))
                except (FileNotFoundError, PermissionError):
                    break  # Scanning can happen concurrently
                except OSError as e:
                    if e.errno == errno.ENOTEMPTY:
                        break
                    raise
                possibly_empty_folder = os.path.dirname(possibly_empty_folder)

            result_tag_attr = "src" if self.outlining == "script" else "href"

            start_tag_attrs = self.start_tag_attrs
            # we purposely keep the leading slash
            target_path = self.outlining_to_path[
                len(os.path.join("src", "public")) :
            ].replace(os.path.sep, "/")

            # prevent the hasher from marking the generated src file as a dependency
            if self.mode == "scan":
                target_path += "?v=tmp&pv=1"
            else:
                out_path = (
                    os.path.join(
                        self.context.folder,
                        self.script_out_folder,
                        f"{self.script_outline_count}.js",
                    )
                    if self.outlining == "script"
                    else os.path.join(
                        self.context.folder,
                        self.style_out_folder,
                        f"{self.style_outline_count}.css",
                    )
                )
                with open(out_path + ".hash", "r") as f:
                    target_hash = f.read()
                target_path += "?" + urlencode(
                    {"v": target_hash, "pv": PROCESSOR_VERSION}
                )

            start_tag_attrs[result_tag_attr] = target_path
            if self.outlining == "style":
                start_tag_attrs["rel"] = "stylesheet"

            data = dict(
                ((None, key), start_tag_attrs[key])
                for key in sorted(start_tag_attrs.keys())
            )

            if self.outlining == "script":
                result = [
                    tkn.HTMLToken(type="StartTag", name="script", data=data),
                    tkn.HTMLToken(type="EndTag", name="script"),
                ]
            else:
                result = [tkn.HTMLToken(type="EmptyTag", name="link", data=data)]

            self.outlining = None
            self.outlining_to_path = None
            self.start_tag_attrs = None
            return result

        assert node["type"] in ("Characters", "SpaceCharacters"), node
        self.outlining_to.write(node["data"])
        return None

    def _should_outline_script(self, node: tkn.HTMLToken) -> bool:
        return (
            node["type"] == "StartTag"
            and node["name"] == "script"
            and (None, "src") not in node["data"]
        )

    def _should_outline_style(self, node: tkn.HTMLToken) -> bool:
        return node["type"] == "StartTag" and node["name"] == "style"

    def scan_result(self) -> ScanFileResult:
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        return BuildFileResult(
            children=list(self.children),
            produced=list(self.produced),
            reused=list(self.reused),
        )
