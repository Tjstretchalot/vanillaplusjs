"""This module applies the standard js manipulators to the document,
stores that in the output directory (as if it were copied), and then
hashes that output as if via hash.
"""

from typing import List
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.js.manips.hash_imports import (
    HashImportsManipulator,
)
import vanillaplusjs.build.handlers.copy
import vanillaplusjs.build.handlers.hash
from vanillaplusjs.build.js.manipulate_and_serialize import manipulate_and_serialize
from vanillaplusjs.build.scan_file_result import ScanFileResult
import os


MANIPULATORS = [
    HashImportsManipulator,
]
"""The manipulators to apply to the document. Each manipulator is a subclass
of JSManipulator whose init function accepts
`(context: BuildContext, relpath: str, mode: Literal["scan", "build"])`

And the manipulator should also implement
`scan_result(self) -> ScanFileResult`
and `build_result(self) -> BuildFileResult`
"""


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    if not relpath.endswith(".js"):
        return ScanFileResult([], [])

    dependencies = set()
    produces = set()

    manips = [manip(context, relpath, "scan") for manip in MANIPULATORS]
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
    if not relpath.endswith(".js"):
        return BuildFileResult([], [], [])

    target_path = vanillaplusjs.build.handlers.copy.get_target_path(context, relpath)

    children = set()
    produced = set()
    reused = set()

    manips = [manip(context, relpath, "build") for manip in MANIPULATORS]

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
        reused.update(build_result.reused)

    return BuildFileResult(
        children=list(children), produced=list(produced), reused=list(reused)
    )


if __name__ == "__main__":
    manipulate_and_serialize(
        "test.js",
        "test.out.js",
        [
            HashImportsManipulator(
                BuildContext(folder=".", dev=False, symlinks=False),
                "test.js",
                "build",
            )
        ],
    )
