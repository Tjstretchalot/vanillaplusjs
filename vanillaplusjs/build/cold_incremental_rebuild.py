from concurrent.futures import ProcessPoolExecutor

import requests
from vanillaplusjs.build.build_context import (
    BuildContext,
    ExternalFile,
    ExternalFileState,
    ExternalFilesState,
)
from vanillaplusjs.build.exceptions import IntegrityMismatchException
from vanillaplusjs.build.ioutil import makedirs_safely
from .graph import FileDependencyGraph
from .file_signature import FileSignature, get_file_signature
from .hot_incremental_rebuild import hot_incremental_rebuild
from loguru import logger
import os
from typing import Dict, Optional, Set, List
import concurrent.futures
import hashlib
from base64 import b64encode
import secrets
import json
import dataclasses


async def cold_incremental_rebuild(
    context: BuildContext,
    old_dependency_graph: FileDependencyGraph,
    old_output_graph: FileDependencyGraph,
    old_placeholders_graph: FileDependencyGraph,
) -> None:
    """Builds the given folder, skipping the standard sanity checks to
    see if the folder has the correct structure.

    Args:
        context (BuildContext): The configuration of the build
        old_dependency_graph (FileDependencyGraph):
            If specified, provides the dependencies of the old build. If
            a file matches the signature in the old dependency graph
            (mtime, size, inode), then we will reuse the old list of
            dependencies rather than having to parse the file in the first
            pass.
        old_output_graph (FileDependencyGraph):
            If specified, provides the outputs of the old build. This is used
            for cleaning the out and artifacts folder of files which are not
            depended on by anyone anymore, and should always be available (prior
            to a build, an empty graph is correct as no outputs have been
            produced). If we rebuild a file and its outputs change, any outputs
            that it used to have which are no longer outputs of any file will be
            deleted.
        old_placeholders_graph (FileDependencyGraph):
            If specified, provides the placeholders of the old build. This is
            used for augmenting the dependency graph: if a depends on b which
            is produced by c, then a depends on c. Placeholders cannot be
            removed once they are added for a file, unless that file is removed,
            in which case we remove the placeholder dependency, effectively
            "upgrading" it, which is not usually desirable but the only logical
            thing to do.
    """
    logger.debug(
        'Starting cold start incremental rebuild on "{}"',
        context.folder,
    )

    await check_external_files(context)

    # This section is to turn a cold start incremental rebuild into a hot
    # start incremental rebuild. When watching a directory we know what
    # files have changed and can use that to inform the build. In a cold
    # start we can determine what files changed using the old graph of
    # file signatures. In both cases, once we know what files have changed,
    # we can start the incremental rebuild.

    relpaths_deleted: Set[str] = set(old_dependency_graph.nodes.keys())
    relpaths_changed: Dict[str, FileSignature] = dict()
    relpaths_added: Dict[str, FileSignature] = dict()

    # PERF:
    #   This is approximately O(1) in the number of src files. There does
    #   not seem to be an obvious way to parallelize this, since the bulk
    #   of the work is listing the files, and we don't know what prefixes
    #   are heavy before starting.

    for (dirpath, _, filenames) in os.walk(context.src_folder):
        for filename in filenames:
            relpath = os.path.relpath(os.path.join(dirpath, filename), context.folder)
            signature = get_file_signature(os.path.join(context.folder, relpath))
            if relpath in old_dependency_graph:
                relpaths_deleted.remove(relpath)
                if not old_dependency_graph.check_file(
                    relpath, signature.filesize, signature.mtime, signature.inode
                ):
                    relpaths_changed[relpath] = signature
            else:
                relpaths_added[relpath] = signature

    logger.info(
        "Cold start incremental build detected {} changed files, {} added files, and {} deleted files",
        len(relpaths_changed),
        len(relpaths_added),
        len(relpaths_deleted),
    )

    await hot_incremental_rebuild(
        context,
        old_dependency_graph,
        old_output_graph,
        old_placeholders_graph,
        relpaths_changed,
        relpaths_added,
        relpaths_deleted,
    )


async def check_external_files(context: BuildContext):
    """Scans the external files in the build; if any of them are out of date
    or missing, they are updated from the url.

    Args:
        context (BuildContext): The context to build in
    """
    if not context.external_files:
        return

    external_files_state = ExternalFilesState(state_by_relpath=dict())
    if os.path.exists(context.external_files_state_file):
        with open(context.external_files_state_file, "r") as f:
            external_files_state = ExternalFilesState.from_json(json.load(f))

    logger.info("Checking external files")

    new_external_files_state = ExternalFilesState(state_by_relpath=dict())

    for old_external_file_relpath in external_files_state.state_by_relpath.keys():
        if old_external_file_relpath not in context.external_files:
            logger.info("Deleting old external file {}", old_external_file_relpath)
            os.remove(os.path.join(context.folder, old_external_file_relpath))

    executor: Optional[ProcessPoolExecutor] = None
    # We don't want to spin up a whole process pool unless we actually have
    # something to do

    futures: List[concurrent.futures.Future] = []
    try:
        for desired_external_file in context.external_files.values():
            if is_external_file_skippable(
                context, external_files_state, desired_external_file.relpath
            ):
                new_external_files_state.state_by_relpath[
                    desired_external_file.relpath
                ] = external_files_state.state_by_relpath[desired_external_file.relpath]
                continue

            if executor is None:
                executor = ProcessPoolExecutor()

            futures.append(
                executor.submit(handle_external_file, context, desired_external_file)
            )
    finally:
        if executor is not None:
            executor.shutdown(wait=True)

    if not futures:
        return

    for future in futures:
        future.result()

    for desired_external_file in context.external_files.values():
        if (
            desired_external_file.relpath
            not in new_external_files_state.state_by_relpath
        ):
            new_external_files_state.state_by_relpath[
                desired_external_file.relpath
            ] = ExternalFileState(
                relpath=desired_external_file.relpath,
                integrity=desired_external_file.integrity,
                signature=get_file_signature(
                    os.path.join(context.folder, desired_external_file.relpath)
                ),
            )

    external_files_state_folder = os.path.dirname(context.external_files_state_file)
    makedirs_safely(external_files_state_folder)
    with open(context.external_files_state_file, "w") as f:
        json.dump(dataclasses.asdict(new_external_files_state), f)


def is_external_file_skippable(
    context: BuildContext, external_files_state: ExternalFilesState, relpath: str
) -> bool:
    """Quickly checks, using a basic file signature test, if we can skip handling
    the external file at the given path relative to the project root.

    Args:
        context (BuildContext): The context to build in
        relpath (str): The path to check

    Returns:
        bool: True if the file is skippable, False otherwise
    """
    desired_file = context.external_files[relpath]
    old_state = external_files_state.state_by_relpath.get(relpath)
    if old_state is None:
        return False

    if old_state.integrity != desired_file.integrity:
        return False

    try:
        new_signature = get_file_signature(os.path.join(context.folder, relpath))
    except FileNotFoundError:
        return False

    return new_signature == old_state.signature


def handle_external_file(
    context: BuildContext,
    external_file: ExternalFile,
):
    """Checks if the file at the given path relative to the project root
    matches the desired integrity. If it does not, updates it from source.

    Raises:
        IntegrityMismatchException: If, after downloading the file from
            the URL, the integrity still does not match.
    """
    try:
        ensure_integrity(
            os.path.join(context.folder, external_file.relpath), external_file.integrity
        )
        return
    except (FileNotFoundError, IntegrityMismatchException):
        pass

    logger.info(
        "Downloading external file {} from {}", external_file.relpath, external_file.url
    )

    makedirs_safely(context.out_folder)
    temp_path = os.path.join(context.out_folder, f"{secrets.token_urlsafe(8)}.tmp")
    try:
        response = requests.get(external_file.url, stream=True)
        response.raise_for_status()
        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        ensure_integrity(temp_path, external_file.integrity)
        try:
            os.unlink(os.path.join(context.folder, external_file.relpath))
        except FileNotFoundError:
            pass
        makedirs_safely(
            os.path.dirname(os.path.join(context.folder, external_file.relpath))
        )
        os.rename(temp_path, os.path.join(context.folder, external_file.relpath))
        logger.info("Downloaded external file {}", external_file.relpath)
    finally:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass


def ensure_integrity(filepath: str, integrity: str) -> None:
    """Checks if the file at the given path matches the given integrity
    string.

    Args:
        filepath (str): The path to the file to check
        integrity (str): The integrity string to check against

    Raises:
        FileNotFoundError: If the file does not exist
        IntegrityMismatchException: If the file does not match the integrity
    """
    (digest_type, expected_digest) = integrity.split("-")
    digest = getattr(hashlib, digest_type)()
    with open(filepath, "rb") as f_in:
        while True:
            data = f_in.read(4096)
            if not data:
                break
            digest.update(data)

    our_digest = b64encode(digest.digest())
    if not bytes(expected_digest, "ascii") == our_digest:
        raise IntegrityMismatchException(
            f"From {filepath} expected {integrity}, got {str(our_digest, 'ascii')}"
        )
