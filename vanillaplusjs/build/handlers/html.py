"""This module applies the standard html manipulators to the document,
stores that in the output directory (as if it were copied), and then
hashes that output as if via hash.
"""

from typing import List, Literal
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.html.manips.images.manip import ImagesManipulator
from vanillaplusjs.build.html.manips.link_rel_canonical import (
    LinkRelCanonicalManipulator,
)
from vanillaplusjs.build.html.manips.link_hash import (
    LinkHash,
)
import vanillaplusjs.build.handlers.copy
import vanillaplusjs.build.handlers.hash
from vanillaplusjs.build.html.manips.outline import OutlineManipulator
from vanillaplusjs.build.html.manips.template import TemplateManipulator
from vanillaplusjs.build.html.manipulate_and_serialize import manipulate_and_serialize
from vanillaplusjs.build.scan_file_result import ScanFileResult
import os


def manipulators(
    context: BuildContext, relpath: str, mode: Literal["scan", "build"]
) -> list:
    """The manipulators to apply to the document. Each manipulator is a duck-typed
    instance of of HTMLManipulator

    And the manipulator should also implement
    `scan_result(self) -> ScanFileResult`
    and `build_result(self) -> BuildFileResult`
    """
    import vanillaplusjs.build.handlers.js
    import vanillaplusjs.build.handlers.css

    return [
        LinkRelCanonicalManipulator(context, relpath, mode),
        LinkHash(context, relpath, mode),
        ImagesManipulator(context, relpath, mode),
        OutlineManipulator(
            context,
            relpath,
            mode,
            vanillaplusjs.build.handlers.js,
            vanillaplusjs.build.handlers.css,
        ),
        TemplateManipulator(context, relpath, mode),
    ]


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    if not relpath.endswith(".html"):
        return ScanFileResult([], [])

    target_path = vanillaplusjs.build.handlers.copy.get_target_path(context, relpath)
    if target_path is None:
        return ScanFileResult([], [])

    dependencies = set()
    produces = set()

    manips = manipulators(context, relpath, "scan")
    manipulate_and_serialize(
        infile=os.path.join(context.folder, relpath), outfile=None, manipulators=manips
    )

    sub_scan_results = [
        vanillaplusjs.build.handlers.copy.scan_file(context, relpath),
        vanillaplusjs.build.handlers.hash.scan_file(context, relpath),
        *[manip.scan_result() for manip in manips],
    ]

    for scan_result in sub_scan_results:
        dependencies.update(scan_result.dependencies)
        produces.update(scan_result.produces)

    return ScanFileResult(dependencies=list(dependencies), produces=list(produces))


def build_file(context: BuildContext, relpath: str) -> BuildFileResult:
    if not relpath.endswith(".html"):
        return BuildFileResult([], [], [])

    target_path = vanillaplusjs.build.handlers.copy.get_target_path(context, relpath)
    if target_path is None:
        return BuildFileResult([], [], [])

    children = set()
    produced = set()
    reused = set()

    manips = manipulators(context, relpath, "build")

    manipulate_and_serialize(
        infile=os.path.join(context.folder, relpath),
        outfile=os.path.join(context.folder, target_path),
        manipulators=manips,
    )

    produced.add(target_path)

    sub_build_results: List[BuildFileResult] = [
        vanillaplusjs.build.handlers.hash.build_file(context, target_path),
        *[manip.build_result() for manip in manips],
    ]

    for build_result in sub_build_results:
        children.update(build_result.children)
        produced.update(build_result.produced)
        for itm in build_result.reused:
            if itm not in produced:
                reused.add(itm)

    return BuildFileResult(
        children=list(children), produced=list(produced), reused=list(reused)
    )
