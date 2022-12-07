from typing import List, Optional, Sequence
import argparse
from loguru import logger
import os
import sys
import json
from vanillaplusjs.build.build_context import (
    BuildContext,
    ExternalFile,
    load_external_files,
    load_js_constants,
)
from vanillaplusjs.build.cold_incremental_rebuild import cold_incremental_rebuild
from vanillaplusjs.build.css.manips.icons.settings import load_icon_settings
from vanillaplusjs.build.html.manips.images.settings import load_image_settings
import vanillaplusjs.constants
from vanillaplusjs.build.graph import FileDependencyGraph
import asyncio


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus build",
        description="Builds the static files, storing them in out/www",
    )
    argparser.add_argument(
        "--dev", action="store_true", help="Build for development specifically"
    )
    argparser.add_argument(
        "--symlinks", action="store_true", help="Force the use of symlinks"
    )
    argparser.add_argument(
        "--no-symlinks", action="store_true", help="Prevent the use of symlinks"
    )
    argparser.add_argument(
        "--folder",
        type=str,
        default=".",
        help=(
            "The base folder to search from. Should contain "
            "src/public and vanillaplus.json. Temporary files "
            "are stored inside at out, and expensive to recreate "
            "files are in artifacts."
        ),
    )
    argparser.add_argument(
        "--delay-files",
        type=str,
        nargs="+",
        help=(
            "This is primarily for debugging. When the given files are "
            "encountered during building, we will delay their processing "
            "a few seconds. This is useful for testing if the build is "
            "time sensitive"
        ),
    )
    args = argparser.parse_args(args)
    symlinks = None
    if args.symlinks:
        symlinks = True
    elif args.no_symlinks:
        symlinks = False
    build(
        args.folder, dev=args.dev, symlinks=symlinks, delay_files=args.delay_files or []
    )


def build(
    folder: str, dev: bool, symlinks: Optional[bool], delay_files: List[str]
) -> None:
    """Builds the static files within the given folder. The folder should
    follow the following structure:

    ```
    src/
        public/
            (html files)
            js/
                (javascript files)
    out/
    artifacts/
    vanillaplusjs.json
    ```

    Then the root folder (which contains src/) is the folder,
    'out' is the where easily recreated files are stored, and 'artifacts'
    is where expensive to recreate files are stored. We will create the out
    and artifacts folders if they do not exist.

    Args:
        folder (str): The folder to build
        dev (bool): Whether to build for development or not
        symlinks (bool, None): If None, we auto-detect symlink support. Otherwise,
            we use the given value.
        delay_files (List[str]): A list of files to delay processing. This is
            primarily for debugging.
    """
    if symlinks is None:
        symlinks = detect_symlink_support()
    context = BuildContext(folder, dev=dev, symlinks=symlinks)
    if not os.path.exists(context.config_file):
        print("Run vanillaplusjs init first")
        sys.exit(1)

    with open(context.config_file) as f:
        config = json.load(f)

    if not isinstance(config, dict):
        print("vanillaplusjs.json should be a JSON object")
        sys.exit(1)

    if config["version"] != vanillaplusjs.constants.CONFIGURATION_VERSION:
        print("vanillaplusjs.json is out of date; please run vanillaplusjs init again")
        sys.exit(1)

    context.host = config["host"]
    if not os.path.exists(context.src_folder):
        print("No src folder found")
        sys.exit(1)

    context.icon_settings = load_icon_settings(context)
    context.image_settings = load_image_settings(config["images"])
    context.auto_generate_images_js_placeholders = config[
        "auto_generate_images_js_placeholders"
    ]
    context.external_files = load_external_files(config["external_files"])
    context.js_constants = load_js_constants(config["js_constants"])
    context.delay_files = delay_files

    old_dependency_graph = FileDependencyGraph()
    # In this graph, all the files in the graph are input files, and input
    # file a is a parent of input file b if the outputs of a depend on b.
    # All files are specified relative to the root folder with no leading
    # slash; e.g., "src/public/index.html".

    old_output_graph = FileDependencyGraph()
    # In this graph, the root files are all input files, but all children
    # are either in out/ or in artifacts/. Furthermore, the maximum depth
    # of this graph is 1. An input file a is a parent of output file b if
    # output file b would be produced exactly as is, so long as a is not
    # modified. Note that a single output file may have multiple input
    # files: for example, an image which is used in multiple places.

    old_placeholders_graph = FileDependencyGraph()
    # In this graph, all the files in the graph are input files, and input
    # file a is a parent of input file b if file b is generated from file a.
    # This is used when we are generating JS files in the out folder, and
    # we want a placeholder file in the src folder containing type hints for
    # the generated file. This augments the dependency graph: if a depends on b
    # which is produced by c, then a depends on c.

    if os.path.exists(context.dependency_graph_file):
        logger.debug("Loading old dependency graph")
        with open(context.dependency_graph_file) as f:
            old_dependency_graph = FileDependencyGraph.load(f)
        logger.debug("Loaded old dependency graph")

    if os.path.exists(context.output_graph_file):
        logger.debug("Loading old outputs graph")
        with open(context.output_graph_file) as f:
            old_output_graph = FileDependencyGraph.load(f)
        logger.debug("Loaded old outputs graph")

    if os.path.exists(context.placeholder_graph_file):
        logger.debug("Loading old placeholders graph")
        with open(context.placeholder_graph_file) as f:
            old_placeholders_graph = FileDependencyGraph.load(f)
        logger.debug("Loaded old placeholders graph")

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            cold_incremental_rebuild(
                context, old_dependency_graph, old_output_graph, old_placeholders_graph
            )
        )

        # Wait for the `ensure_future`s to finish cleanly
        pending = asyncio.all_tasks(loop)
        while pending:
            loop.run_until_complete(
                asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
            )
            pending = asyncio.all_tasks(loop)
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def detect_symlink_support() -> bool:
    try:
        with open("___symlink_test___.txt", "w") as f:
            f.write("test")

        os.symlink("___symlink_test___.txt", "___symlink_test___2.txt")
        return True
    except OSError:
        logger.debug("Symlinks disabled (unsupported)")
        return False
    finally:
        if os.path.exists("___symlink_test___2.txt"):
            os.remove("___symlink_test___2.txt")
        os.remove("___symlink_test___.txt")
