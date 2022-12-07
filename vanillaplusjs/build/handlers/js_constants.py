"""The handler for the JS constants files"""

from typing import Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.css.serializer import serialize_string_auto_quote
import vanillaplusjs.build.handlers.copy
import vanillaplusjs.build.handlers.hash
from vanillaplusjs.build.ioutil import makedirs_safely
from vanillaplusjs.build.scan_file_result import ScanFileResult
import os


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    if relpath != context.js_constants.relpath:
        return ScanFileResult(dependencies=[], produces=[])

    target_path = vanillaplusjs.build.handlers.copy.get_target_path(context, relpath)
    assert target_path is not None, "JS constants file would not be copied"
    return ScanFileResult(
        dependencies=[], produces=[target_path, target_path + ".hash"]
    )


def build_file(context: BuildContext, relpath: str) -> BuildFileResult:
    if relpath != context.js_constants.relpath:
        return BuildFileResult(children=[], produced=[], reused=[])

    children: Set[str] = set()
    produced: Set[str] = set()
    reused: Set[str] = set()

    target_relpath = vanillaplusjs.build.handlers.copy.get_target_path(context, relpath)
    target_path = os.path.join(context.folder, target_relpath)
    if os.path.exists(target_path):
        reused.add(target_relpath)
    else:
        produced.add(target_relpath)

        constants = context.js_constants.shared.copy()
        if context.dev:
            constants.update(context.js_constants.dev)
        else:
            constants.update(context.js_constants.prod)

        makedirs_safely(os.path.dirname(target_path))
        with open(target_path, "w", newline="\n") as f:
            if not constants:
                f.write("\n")
            for key, value in constants.items():
                f.write(f"export const {key} = {jsify(value)};\n")

    build_result = vanillaplusjs.build.handlers.hash.build_file(context, target_relpath)
    children.update(build_result.children)
    produced.update(build_result.produced)
    reused.update(build_result.reused)

    return BuildFileResult(
        children=list(children), produced=list(produced), reused=list(reused)
    )


def jsify(val) -> str:
    if isinstance(val, str):
        return serialize_string_auto_quote(val)

    if val is True:
        return "true"

    if val is False:
        return "false"

    if isinstance(val, (int, float)):
        return str(val)

    return repr(val)
