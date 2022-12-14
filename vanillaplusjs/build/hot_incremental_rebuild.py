from typing import Dict, List, Literal, Set, Tuple
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.build_file import build_file
from vanillaplusjs.build.exceptions import (
    CyclicDependencyException,
)
from vanillaplusjs.build.file_signature import FileSignature, get_file_signature
from vanillaplusjs.build.ioutil import makedirs_safely
from vanillaplusjs.build.scan_file import scan_file
from vanillaplusjs.build.scan_file_result import ScanFileResult
from .graph import FileDependencyGraph
from loguru import logger
import concurrent.futures
import os
import asyncio
import itertools


async def hot_incremental_rebuild(
    context: BuildContext,
    old_dependency_graph: FileDependencyGraph,
    old_output_graph: FileDependencyGraph,
    old_placeholders_graph: FileDependencyGraph,
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
            If specified, provides the dependencies of the old build. The file
            "parent" is a parent of the file "child" if the outputs of "parent"
            depend on the contents of "child". The dependency graph exclusively
            references source files.
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

    if os.path.exists(os.path.join(context.folder, context.js_constants.relpath)):
        current_mode: Literal["dev", "prod"] = "dev" if context.dev else "prod"
        old_constants_mode = None
        try:
            with open(
                os.path.join(context.out_folder, "js_constants_mode.txt"), "r"
            ) as f:
                old_constants_mode = f.read()
        except FileNotFoundError:
            pass

        if old_constants_mode != current_mode:
            if (context.js_constants.relpath not in changed_files) and (
                context.js_constants.relpath not in added_files
            ):
                logger.debug(
                    f"Marking {context.js_constants.relpath} changed due to new mode {current_mode} (was {old_constants_mode})"
                )
                changed_files[context.js_constants.relpath] = get_file_signature(
                    os.path.join(context.folder, context.js_constants.relpath)
                )

            makedirs_safely(context.out_folder)
            with open(
                os.path.join(context.out_folder, "js_constants_mode.txt"), "w"
            ) as f:
                f.write(current_mode)
    else:
        try:
            os.unlink(os.path.join(context.out_folder, "js_constants_mode.txt"))
        except FileNotFoundError:
            pass

    if not changed_files and not added_files and not deleted_files:
        logger.info("Nothing to do, exiting")
        return

    with concurrent.futures.ProcessPoolExecutor() as executor:
        files_that_need_scanning = list(changed_files.keys()) + list(added_files.keys())
        updated_children: Dict[str, ScanFileResult] = dict()
        new_placeholders: Dict[str, str] = dict()  # placeholder -> original file

        while files_that_need_scanning:
            additional_children: Dict[str, ScanFileResult] = await scan_files(
                context, executor, files_that_need_scanning
            )

            updated_children.update(additional_children)

            files_that_need_scanning = []
            for scanned_file_relpath, scan_result in additional_children.items():
                if scan_result.placeholders:
                    for (
                        placeholder_relpath,
                        placeholder_contents,
                    ) in scan_result.placeholders.items():
                        if os.path.exists(
                            os.path.join(context.folder, placeholder_relpath)
                        ):
                            continue

                        logger.info(
                            "{} generated a placeholder file {}",
                            scanned_file_relpath,
                            placeholder_relpath,
                        )
                        with open(
                            os.path.join(context.folder, placeholder_relpath), "w"
                        ) as f:
                            f.write(placeholder_contents)
                        files_that_need_scanning.append(placeholder_relpath)
                        new_placeholders[placeholder_relpath] = scanned_file_relpath
                        added_files[placeholder_relpath] = get_file_signature(
                            os.path.join(context.folder, placeholder_relpath)
                        )

        # When the scan file result marks an output file as a dependency,
        # we must reinterpret that as a dependency on a file which intends
        # to produce that output file.

        out_dependencies_mapping: Dict[str, str] = dict()
        for scanned_file_relpath, scan_result in updated_children.items():
            logger.debug(
                f"{scanned_file_relpath} depends on {scan_result.dependencies}"
            )
            logger.debug(f"{scanned_file_relpath} produces {scan_result.produces}")
            for out_relpath in scan_result.produces:
                out_dependencies_mapping[out_relpath] = scanned_file_relpath

        for scanned_file_relpath, scan_result in updated_children.items():
            new_dependencies = set()

            for dep_relpath in scan_result.dependencies:
                if not any(
                    dep_relpath.startswith(prefix) for prefix in ("out", "artifacts")
                ):
                    new_dependencies.add(dep_relpath)
                    continue

                if dep_relpath in out_dependencies_mapping:
                    new_dependencies.add(out_dependencies_mapping[dep_relpath])
                    continue

                if dep_relpath not in out_dependencies_mapping:
                    if dep_relpath not in old_output_graph:
                        raise ValueError(
                            f"{scanned_file_relpath=} depends on {dep_relpath=}, but nothing produces that file!"
                        )
                    produced_by = old_output_graph.get_parents(dep_relpath)
                    # take the first one which hasn't been deleted
                    for p in produced_by:
                        if p not in deleted_files:
                            out_dependencies_mapping[dep_relpath] = p
                            new_dependencies.add(p)
                            break
                    else:
                        raise ValueError(
                            f"{scanned_file_relpath=} depends on {dep_relpath=}, but all the files which produce that file have been deleted!"
                        )

            new_dependencies.discard(scanned_file_relpath)
            logger.debug(
                f"after transformations, {scanned_file_relpath} depends on {new_dependencies}"
            )
            scan_result.dependencies = list(new_dependencies)

        files_to_rebuild: Set[str] = set()
        dirtied_outputs: Set[str] = set()
        dirtied_artifacts: Set[str] = set()
        stack: List[str] = []

        for file in updated_children.keys():
            files_to_rebuild.add(file)
            stack.append(file)

        for file in deleted_files:
            files_to_rebuild.add(file)
            stack.append(file)

        while stack:
            file = stack.pop()

            if file in old_dependency_graph:
                for par in old_dependency_graph.get_parents(file):
                    if par not in files_to_rebuild:
                        files_to_rebuild.add(par)
                        stack.append(par)

            if file in old_placeholders_graph:
                for par in old_placeholders_graph.get_parents(file):
                    if par not in files_to_rebuild:
                        files_to_rebuild.add(par)
                        stack.append(par)

            if file in old_output_graph:
                for child in old_output_graph.get_children(file):
                    if child.startswith("artifacts"):
                        dirtied_artifacts.add(child)
                    else:
                        dirtied_outputs.add(child)

        files_to_rebuild = [
            file for file in files_to_rebuild if file not in deleted_files
        ]
        original_files_to_rebuild = frozenset(files_to_rebuild)

        logger.debug("{} files to rebuild", len(files_to_rebuild))
        logger.debug("{} files to clean", len(dirtied_outputs))
        logger.debug("{} files to possibly clean", len(dirtied_artifacts))

        possibly_empty_folders = set()
        for file in itertools.chain(dirtied_outputs, dirtied_artifacts):
            folder = os.path.dirname(file)
            while folder != "":
                possibly_empty_folders.add(folder)
                folder = os.path.dirname(folder)

        for file in dirtied_outputs:
            logger.debug("Cleaning {}", file)
            try:
                os.unlink(os.path.join(context.folder, file))
            except FileNotFoundError:
                logger.warning(
                    "Expected output {} to exist so we could clean it, but it did not. Continuing..",
                    file,
                )

        updated_results: Dict[str, BuildFileResult] = dict()
        pending_results: Dict[str, asyncio.Future] = dict()
        still_dirty_outputs = set(dirtied_outputs)
        pending_dirty_outputs = set()
        still_dirty_artifacts = set(dirtied_artifacts)
        pending_artifacts = set()

        def get_file_depends_on(file: str) -> List[str]:
            if file in updated_children:
                updated_result = updated_children[file]
                if file in new_placeholders:
                    return updated_result.dependencies + [new_placeholders[file]]
                if file in old_placeholders_graph:
                    return (
                        updated_result.dependencies
                        + old_placeholders_graph.get_parents(file)
                    )
                return updated_result.dependencies

            if file not in old_placeholders_graph:
                return old_dependency_graph.get_children(file)
            return old_dependency_graph.get_children(
                file
            ) + old_placeholders_graph.get_parents(file)

        def get_file_creates(file: str) -> List[str]:
            if file in updated_children:
                updated_result = updated_children[file]
                return updated_result.produces
            if file in old_output_graph:
                return old_output_graph.get_children(file)
            return []

        while files_to_rebuild or pending_results:
            rebuildable_files: List[str] = []
            for file in files_to_rebuild:
                file_depends_on: List[str] = get_file_depends_on(file)
                file_creates: List[str] = get_file_creates(file)

                logger.debug(
                    f"considering starting {file} {file_depends_on=} {file_creates=}"
                )

                all_dependencies_built = True
                for child in file_depends_on:
                    if (
                        child not in updated_results
                        and child in original_files_to_rebuild
                    ):
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
                    if output in pending_dirty_outputs or output in pending_artifacts:
                        all_outputs_not_pending = False
                        logger.debug(
                            "Cannot rebuild {} while we are cleaning {}",
                            file,
                            output,
                        )

                if not all_outputs_not_pending:
                    continue

                rebuildable_files.append(file)
                for output in file_creates:
                    if output in still_dirty_outputs:
                        pending_dirty_outputs.add(output)
                    elif output in dirtied_artifacts:
                        pending_artifacts.add(output)

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

                    reinterpreted_children: List[str] = []
                    for child in rebuild_result.children:
                        if child in out_dependencies_mapping:
                            mapped_child = out_dependencies_mapping[child]
                            if mapped_child != pending_file:
                                reinterpreted_children.append(mapped_child)
                        elif child.startswith("out") or child.startswith("artifacts"):
                            found = False
                            inner_seen = set()
                            if pending_file not in updated_children:
                                # the output probably came from one of its dependencies, lets search
                                # for it
                                inner_stack: List[str] = [pending_file]
                                while inner_stack:
                                    inner_file = inner_stack.pop()
                                    for produced in old_output_graph.get_children(
                                        inner_file
                                    ):
                                        if produced == child:
                                            out_dependencies_mapping[child] = inner_file
                                            if inner_file != pending_file:
                                                reinterpreted_children.append(
                                                    inner_file
                                                )
                                            found = True
                                            break
                                    if found:
                                        break
                                    for (
                                        inner_child
                                    ) in old_dependency_graph.get_children(inner_file):
                                        if inner_child not in inner_seen:
                                            inner_stack.append(inner_child)
                                            inner_seen.add(inner_child)

                            if not found:
                                raise ValueError(
                                    f"{pending_file} lists {child} as a child, which is in the out folder, "
                                    f"but we cannot find who produced it; checked {inner_seen}"
                                )
                        else:
                            reinterpreted_children.append(child)
                    rebuild_result.children = reinterpreted_children

                    updated_results[pending_file] = rebuild_result
                    del pending_results[pending_file]
                    for file in rebuild_result.produced:
                        if file in still_dirty_outputs:
                            logger.debug("Cleaned {} using {}", file, pending_file)
                            still_dirty_outputs.remove(file)
                            pending_dirty_outputs.remove(file)
                        elif file in still_dirty_artifacts:
                            logger.debug("Cleaned {} using {}", file, pending_file)
                            still_dirty_artifacts.remove(file)
                            pending_artifacts.remove(file)
                        elif file in dirtied_artifacts:
                            logger.debug("Updated {} using {}", file, pending_file)
                            pending_artifacts.remove(file)
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
                        elif file in still_dirty_artifacts:
                            logger.debug(
                                "Determined {} is not dirty using {}",
                                file,
                                pending_file,
                            )
                            still_dirty_artifacts.remove(file)
                            pending_artifacts.remove(file)
                        elif file in dirtied_artifacts:
                            logger.debug("Reused {} in {}", file, pending_file)
                            pending_artifacts.remove(file)
                        else:
                            logger.debug("Reused {} for {}", file, pending_file)

        logger.debug("Finished rebuilding {} files", len(updated_results))

        for file in still_dirty_artifacts:
            logger.debug("Cleaning {}", file)
            os.unlink(os.path.join(context.folder, file))

        for folder_relpath in sorted(possibly_empty_folders, key=lambda s: -len(s)):
            folder = os.path.join(context.folder, folder_relpath)
            scandir_iter = os.scandir(folder)
            has_any_contents = next(scandir_iter, None) is not None
            scandir_iter.close()
            if not has_any_contents:
                logger.debug("Cleaning empty folder {}", folder_relpath)
                os.rmdir(folder)

        new_dependency_graph = FileDependencyGraph()
        new_output_graph = FileDependencyGraph()
        new_placeholder_graph = FileDependencyGraph()

        all_input_files = list(
            f
            for f in frozenset(
                list(updated_results.keys()) + list(old_dependency_graph.nodes.keys())
            )
            if f not in deleted_files
        )

        possible_empty_placeholder_nodes = set()
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
            new_placeholder_graph.add_file(
                file, new_signature.filesize, new_signature.mtime, new_signature.inode
            )
            possible_empty_placeholder_nodes.add(file)

        possibly_empty_output_nodes = set()
        for file, node in old_output_graph.nodes.items():
            if file not in new_output_graph:
                old_parents = old_output_graph.get_parents(file)

                if old_parents:
                    # this is produced file; we can delete it from the graph if
                    # nothing else is now producing it
                    if any(p in deleted_files for p in old_parents) and not any(
                        p not in deleted_files and p not in updated_results
                        for p in old_parents
                    ):
                        possibly_empty_output_nodes.add(file)
                else:
                    # this is a consumed file; we only need it if it still exists
                    if file in deleted_files:
                        continue

                new_output_graph.add_file(file, node.filesize, node.mtime, node.inode)

        for file, node in old_placeholders_graph.nodes.items():
            if file not in new_placeholder_graph:
                # either:
                #  - file used to generate a placeholder, but now that file
                #    has been deleted, the placeholders are now full-blown
                #    files
                #  - file was generated by generator, file was deleted, and
                #    the generator did not reproduce it
                continue

            old_generators_of_file = old_placeholders_graph.get_parents(file)

            for generator in old_generators_of_file:
                if generator in new_placeholder_graph:
                    # generator still exists, so this file is still a placeholder
                    new_placeholder_graph.set_children(
                        generator,
                        new_placeholder_graph.get_children(generator) + [file],
                    )
                    possible_empty_placeholder_nodes.remove(generator)
                    possible_empty_placeholder_nodes.remove(file)
                    break

        for placeholder, generator in new_placeholders.items():
            gen_children = new_placeholder_graph.get_children(generator)
            if placeholder not in gen_children:
                gen_children.append(placeholder)
            new_placeholder_graph.set_children(generator, gen_children)

        for file in all_input_files:
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

        for node in possibly_empty_output_nodes:
            if not new_output_graph.get_parents(node):
                new_output_graph.remove_file(node)

        for node in possible_empty_placeholder_nodes:
            if not new_placeholder_graph.get_parents(
                node
            ) and not new_placeholder_graph.get_children(node):
                new_placeholder_graph.remove_file(node)

        logger.debug(
            "Finished constructing new dependency, output, and placeholder graphs"
        )

        makedirs_safely(context.out_folder)

        with open(context.dependency_graph_file, "w") as fp:
            new_dependency_graph.store(fp)

        with open(context.output_graph_file, "w") as fp:
            new_output_graph.store(fp)

        with open(context.placeholder_graph_file, "w") as fp:
            new_placeholder_graph.store(fp)

        logger.debug("Finished storing dependency, output, and placeholder graphs")
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
