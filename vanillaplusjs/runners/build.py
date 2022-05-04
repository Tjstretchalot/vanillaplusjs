from typing import Sequence
import argparse
from loguru import logger
import os
import sys
import json
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.cold_incremental_rebuild import cold_incremental_rebuild
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
    args = argparser.parse_args(args)
    build(
        args.folder,
        dev=args.dev,
    )


def build(folder: str, dev: bool) -> None:
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
    """
    context = BuildContext(folder, dev=dev, symlinks=detect_symlink_support())
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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        cold_incremental_rebuild(context, old_dependency_graph, old_output_graph)
    )

    # Wait for the `ensure_future`s to finish cleanly
    pending = asyncio.all_tasks(loop)
    while pending:
        loop.run_until_complete(
            asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
        )
        pending = asyncio.all_tasks(loop)

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
