from vanillaplusjs.build.build_context import BuildContext
from .graph import FileDependencyGraph
from .file_signature import FileSignature, get_file_signature
from .hot_incremental_rebuild import hot_incremental_rebuild
from loguru import logger
import os
from typing import Dict, Set


async def cold_incremental_rebuild(
    context: BuildContext,
    old_dependency_graph: FileDependencyGraph,
    old_output_graph: FileDependencyGraph,
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
    """
    logger.debug(
        'Starting cold start incremental rebuild on "{}"',
        context.folder,
    )

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

    if not relpaths_deleted and not relpaths_changed and not relpaths_added:
        logger.info("No changes detected, nothing to do.")
        return

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
        relpaths_changed,
        relpaths_added,
        relpaths_deleted,
    )
