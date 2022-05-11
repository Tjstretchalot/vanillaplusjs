"""This module describes the scan and build logic for simply copying
a file over.
"""
import os
from typing import Optional
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
import shutil


def get_target_path(context: BuildContext, relpath: str) -> Optional[str]:
    """Determines where to copy the file to, if the file should be copied,
    otherwise returns None
    """
    # A lot of the path related functions here are shockingly slow, hence
    # this is a bit of a hack to make scanning faster
    rel_public_folder = f"src{os.path.sep}public"
    if not relpath.startswith(rel_public_folder):
        return None
    relative_to_public_folder = relpath[len(rel_public_folder) + len(os.path.sep) :]
    return f"out{os.path.sep}www{os.path.sep}{relative_to_public_folder}"


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    target_path = get_target_path(context, relpath)
    if target_path is None:
        return ScanFileResult(dependencies=[], produces=[])

    return ScanFileResult(dependencies=[], produces=[target_path])


def build_file(context: BuildContext, relpath: str) -> BuildFileResult:
    target_path = get_target_path(context, relpath)
    if target_path is None:
        return BuildFileResult(children=[], produced=[], reused=[])

    src_path_rel_to_cwd = os.path.join(context.folder, relpath)
    target_path_rel_to_cwd = os.path.join(context.folder, target_path)

    if os.path.exists(target_path_rel_to_cwd):
        return BuildFileResult(children=[], produced=[], reused=[target_path])

    os.makedirs(os.path.dirname(target_path_rel_to_cwd), exist_ok=True)

    if context.symlinks:
        os.symlink(
            os.path.abspath(src_path_rel_to_cwd),
            target_path_rel_to_cwd,
        )
    else:
        shutil.copyfile(
            src_path_rel_to_cwd,
            target_path_rel_to_cwd,
        )

    return BuildFileResult(children=[], produced=[target_path], reused=[])
