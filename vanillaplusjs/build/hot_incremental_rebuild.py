from typing import Dict, List, Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file import BuildFileResult, build_file
from vanillaplusjs.build.exceptions import (
    CyclicDependencyException,
    MissingConfigurationException,
)
from vanillaplusjs.build.file_signature import FileSignature, get_file_signature
from vanillaplusjs.build.scan_file import ScanFileResult, scan_file
from .graph import FileDependencyGraph
from loguru import logger
import concurrent.futures
import os
import asyncio


async def hot_incremental_rebuild(
    context: BuildContext,
    old_dependency_graph: FileDependencyGraph,
    old_output_graph: FileDependencyGraph,
    changed_files: Dict[str, FileSignature],
    added_files: Dict[str, FileSignature],
    deleted_files: List[str],
) -> None:
    """Performs a hot incremental rebuild; this refers to a rebuild where
    the files that changed have already been determined, and hence this only
    scales based on the number of files that must be rebuilt, rather than the
    total number of files in the project.

    Paths (such as in changed_files) should be specified relative to the folder
    with no leading slashes, e.g., "src/public/index.html"

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
        changed_files (dict[str, FileSignature]):
            The list of files that are in the old dependency graph, but whose
            contents may have changed. These files will be rebuilt, and if their
            outputs change, any outputs that they used to have which are no
            longer outputs of any file will be deleted. When we store the new
            dependency graph, we will use the given file signature, which could
            matter if the file is updated while we are rebuilding.
        added_files (dict[str, FileSignature]):
            The list of files that are not in the old dependency graph, but
            which have been added to the project. These files will be parsed and
            their dependencies and outputs will be added to the dependency and
            output graphs respectively. When we store the new dependency graph,
            we will use the given file signature, which could matter if the file
            is updated while we are rebuilding.
        deleted_files (list[str]):
            The list of files that are in the old dependency graph, but which
            have been deleted from the project. These files will be removed
            from the dependency graph, and if they are in the output graph,
            their outputs will be removed from the output graph and they will
            be checked for whether they are outputs of any file.
    """
    logger.info(
        "Starting hot incremental rebuild of {} changed files, "
        "{} added files, and {} deleted files at {}",
        len(changed_files),
        len(added_files),
        len(deleted_files),
        context.folder,
    )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        updated_children: Dict[str, ScanFileResult] = await scan_files(
            context,
            executor,
            list(changed_files.keys()) + list(added_files.keys()),
        )

        files_to_rebuild: Set[str] = set()
        dirtied_outputs: Set[str] = set()
        stack: List[str] = []

        for file, new_info in updated_children.items():
            stack.append(file)
            stack.extend(new_info.dependencies)

        for file in deleted_files:
            stack.append(file)

        while stack:
            file = stack.pop()
            if file in files_to_rebuild:
                continue
            files_to_rebuild.add(file)

            if file in old_dependency_graph:
                for par in old_dependency_graph.get_parents(file):
                    if par not in files_to_rebuild:
                        stack.append(par)

            if file in old_output_graph:
                for child in old_output_graph.get_children(file):
                    dirtied_outputs.add(child)

        files_to_rebuild = [
            file for file in files_to_rebuild if file not in deleted_files
        ]

        logger.debug("{} files to rebuild", len(files_to_rebuild))
        logger.debug("{} files to clean", len(dirtied_outputs))

        for file in dirtied_outputs:
            logger.debug("Cleaning {}", file)
            os.unlink(os.path.join(context.folder, file))

        updated_results: Dict[str, BuildFileResult] = dict()
        pending_results: Dict[str, asyncio.Future] = dict()
        still_dirty_outputs = set(dirtied_outputs)
        pending_dirty_outputs = set()

        while files_to_rebuild:
            rebuildable_files: List[str] = []
            for file in files_to_rebuild:
                file_depends_on: List[str] = None
                file_creates: List[str] = None

                if file in updated_children:
                    updated_result = updated_children[file]
                    file_depends_on = updated_result.dependencies
                    file_creates = updated_result.produces
                else:
                    file_depends_on = old_dependency_graph.get_children(file)
                    if file in old_output_graph:
                        file_creates = old_output_graph.get_children(file)
                    else:
                        file_creates = []

                all_dependencies_built = True
                for child in file_depends_on:
                    if child not in updated_results and child in files_to_rebuild:
                        logger.debug(
                            "Cannot rebuild {} until we have rebuilt {}",
                            file,
                            child,
                        )
                        all_dependencies_built = False
                        break

                if not all_dependencies_built:
                    continue

                all_outputs_not_pending = True
                for output in file_creates:
                    if output in pending_dirty_outputs:
                        logger.debug(
                            "Cannot rebuild {} until we have finished cleaning {}",
                            file,
                            output,
                        )

                if not all_outputs_not_pending:
                    continue

                rebuildable_files.append(file)
                for output in file_creates:
                    if output in still_dirty_outputs:
                        pending_dirty_outputs.add(output)

            if not rebuildable_files and not pending_results:
                logger.error("No files to rebuild")
                raise CyclicDependencyException(
                    "No files to rebuild. This is likely due to a cyclic "
                    "dependency in the project. In particular, we did not find any "
                    "buildable files in the following files: {}".format(
                        ", ".join(files_to_rebuild)
                    )
                )

            for file in rebuildable_files:
                logger.debug("Queueing {} to be rebuilt asynchronously", file)
                files_to_rebuild.remove(file)
                concurrency_future_result = executor.submit(build_file, context, file)
                pending_results[file] = asyncio.wrap_future(concurrency_future_result)

            await asyncio.wait(
                pending_results.values(), return_when=asyncio.FIRST_COMPLETED
            )
            for pending_file in list(pending_results.keys()):
                future = pending_results[pending_file]
                if future.done():
                    logger.debug("Finished rebuilding {}", pending_file)
                    rebuild_result: BuildFileResult = future.result()
                    updated_results[pending_file] = rebuild_result
                    del pending_results[pending_file]
                    for file in rebuild_result.produced:
                        if file in still_dirty_outputs:
                            logger.debug("Cleaned {} using {}", file, pending_file)
                            still_dirty_outputs.remove(file)
                            pending_dirty_outputs.remove(file)
                        else:
                            logger.debug("Produced {} from {}", file, pending_file)
                    for file in rebuild_result.reused:
                        if file in still_dirty_outputs:
                            logger.warning(
                                "Reused {} despite being dirty; this is likely a bug",
                                file,
                            )
                            still_dirty_outputs.remove(file)
                            pending_dirty_outputs.remove(file)
                        else:
                            logger.debug("Reused {} for {}", file, pending_file)

        logger.debug("Finished rebuilding {} files", len(updated_results))

        new_dependency_graph = FileDependencyGraph()
        new_output_graph = FileDependencyGraph()

        all_input_files = list(
            f
            for f in frozenset(
                list(updated_results.keys()) + list(old_dependency_graph.nodes.keys())
            )
            if f not in deleted_files
        )

        for file in all_input_files:
            new_signature: FileSignature = None
            if file in changed_files:
                new_signature = changed_files[file]
            elif file in added_files:
                new_signature = added_files[file]
            else:
                old_node = old_dependency_graph.nodes[file]
                new_signature = FileSignature(
                    old_node.mtime, old_node.filesize, old_node.inode
                )

            new_dependency_graph.add_file(
                file, new_signature.filesize, new_signature.mtime, new_signature.inode
            )
            new_output_graph.add_file(
                file, new_signature.filesize, new_signature.mtime, new_signature.inode
            )

        for file, node in old_output_graph.nodes.items():
            if file not in new_output_graph:
                new_output_graph.add_file(file, node.filesize, node.mtime, node.inode)

        for file in list(updated_results.keys()) + list(
            old_dependency_graph.nodes.keys()
        ):
            new_dependencies = (
                updated_results[file].children
                if file in updated_results
                else old_dependency_graph.get_children(file)
            )
            new_dependency_graph.set_children(
                file,
                children=new_dependencies,
            )

            new_outputs: List[str] = None
            if file in updated_results:
                updated_result = updated_results[file]
                new_outputs = updated_result.produced + updated_result.reused
            elif file in old_output_graph:
                new_outputs = old_output_graph.get_children(file)
            else:
                new_outputs = []

            for output in new_outputs:
                if output not in new_output_graph:
                    signature = get_file_signature(os.path.join(context.folder, output))
                    new_output_graph.add_file(
                        output, signature.filesize, signature.mtime, signature.inode
                    )

            new_output_graph.set_children(
                file,
                new_outputs,
            )

        logger.debug("Finished constructing new dependency and output graphs")

        os.makedirs(context.out_folder, exist_ok=True)

        with open(context.dependency_graph_file, "w") as fp:
            new_dependency_graph.store(fp)

        with open(context.output_graph_file, "w") as fp:
            new_output_graph.store(fp)

        logger.debug("Finished storing dependency and output graphs")
        logger.info('"{}" rebuilt successfully', context.folder)


async def scan_files(
    context: BuildContext, executor: concurrent.futures.Executor, files: List[str]
) -> Dict[str, ScanFileResult]:
    """Asyncronously determines the updated dependencies and artifacts
    to produce for the given files.

    Args:
        context (BuildContext): The context for the build.
        executor (concurrent.futures.Executor): The executor
            for asyncronously scanning the files
        files (list[str]): The files to scan, relative to the folder

    Returns:
        dict[str, list[str]]: A dict mapping from files to their
            dependencies
    """
    updated_children: Dict[str, List[str]] = {}
    if not files:
        return updated_children

    logger.debug("Scanning {} files asynchronously", len(files))
    mapped_file_futures = [
        executor.submit(scan_file, context, relpath) for relpath in files
    ]
    mapped_files = []
    for future in mapped_file_futures:
        mapped_files.append(await asyncio.wrap_future(future))

    return dict(zip(files, mapped_files))
