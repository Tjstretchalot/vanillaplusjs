"""Combination of the copy and hash handlers."""
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
import vanillaplusjs.build.handlers.copy
import vanillaplusjs.build.handlers.hash


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    copy_result = vanillaplusjs.build.handlers.copy.scan_file(context, relpath)
    hash_result = vanillaplusjs.build.handlers.hash.scan_file(context, relpath)

    return ScanFileResult(
        dependencies=copy_result.dependencies + hash_result.dependencies,
        produces=copy_result.produces + hash_result.produces,
    )


def build_file(context: BuildContext, relpath: str) -> BuildFileResult:
    copy_result = vanillaplusjs.build.handlers.copy.build_file(context, relpath)
    hash_result = vanillaplusjs.build.handlers.hash.build_file(context, relpath)

    return BuildFileResult(
        children=copy_result.children + hash_result.children,
        produced=copy_result.produced + hash_result.produced,
        reused=copy_result.reused + hash_result.reused,
    )
