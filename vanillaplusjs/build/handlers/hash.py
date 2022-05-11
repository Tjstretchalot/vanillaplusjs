"""This module provides the scan and build logic for producing a hash
of the contents of a file. Since this is expected to be used for produced
artifacts much of the time, it supports files relative to either the public
or out folder.
"""
import os
from typing import Optional
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult
import hashlib
import base64


def get_target_path(context: BuildContext, relpath: str) -> Optional[str]:
    """Determines where to hash the file to, if the file should be copied,
    otherwise returns None
    """
    # A lot of the path related functions here are shockingly slow, hence
    # this is a bit of a hack to make scanning faster
    possible_parent_folders = [
        f"src{os.path.sep}public{os.path.sep}",
        f"out{os.path.sep}www{os.path.sep}",
    ]

    for parent in possible_parent_folders:
        if relpath.startswith(parent):
            relative_to_parent = relpath[len(parent) :]
            return f"out{os.path.sep}www{os.path.sep}{relative_to_parent}.hash"

    return None


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

    sha256 = hashlib.sha256()
    with open(src_path_rel_to_cwd, "rb") as f:
        sha256.update(f.read())

    sha256_b64 = base64.urlsafe_b64encode(sha256.digest()).decode("utf-8")

    with open(target_path_rel_to_cwd, "w") as f:
        f.write(sha256_b64)

    return BuildFileResult(children=[], produced=[target_path], reused=[])
