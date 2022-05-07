from typing import Sequence, Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.file_signature import get_file_signature
from vanillaplusjs.build.graph import FileDependencyGraph
from vanillaplusjs.build.hot_incremental_rebuild import hot_incremental_rebuild
from .build import build, detect_symlink_support
from .run import run_server
import argparse
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileModifiedEvent,
    FileMovedEvent,
    FileDeletedEvent,
    FileCreatedEvent,
)
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from loguru import logger
import sys
import signal
import threading
import time
import json
import asyncio


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus dev",
        description=(
            "Builds the webserver in development mode and "
            "runs the webserver on the given port"
        ),
    )
    argparser.add_argument(
        "--folder",
        type=str,
        default=".",
        help="The folder containing vanillaplusjs.json",
    )
    argparser.add_argument(
        "--host", type=str, default="localhost", help="The host to run the webserver on"
    )
    argparser.add_argument(
        "--port", type=int, default=8888, help="The port to run the webserver on"
    )
    argparser.add_argument(
        "--watch", action="store_true", help="Watch for changes and rebuild"
    )
    argparser.add_argument(
        "--debounce",
        type=int,
        default=100,
        help="Debounce time in milliseconds after changes are detected",
    )
    args = argparser.parse_args(args)

    dev(
        folder=args.folder,
        host=args.host,
        port=args.port,
        watch=args.watch,
        debounce=args.debounce,
    )


def dev(folder: str, host: str, port: int, watch: bool, debounce: int) -> None:
    """Builds the webserver in development mode and runs the webserver on the
    given port.

    Args:
        host (str): The host to run the webserver on
        port (int): The port to run the webserver on
        watch (bool): Whether to watch for changes and rebuild
    """
    if not os.path.exists(os.path.join(folder, "vanillaplusjs.json")):
        logger.warning(
            'vanillaplusjs.json not found. Call "vanillaplusjs init" to create it.'
        )
        sys.exit(1)

    build(folder=folder, dev=True)
    if not watch:
        return run_server(folder=folder, host=host, port=port)

    abs_cwd = os.path.abspath(os.getcwd())
    abs_folder = os.path.abspath(folder)
    os.chdir(os.path.join(folder, "out", "www"))
    try:
        logger.info(f"Running server on {host}:{port}")
        server = HTTPServer((host, port), SimpleHTTPRequestHandler)

        def handler(signal, frame):
            logger.info("Shutting down server...")
            server.shutdown()

        signal.signal(signal.SIGINT, handler)
        server_thread = threading.Thread(
            target=server.serve_forever, kwargs={"poll_interval": 0.1}
        )
        server_thread.daemon = True
        server_thread.start()

        logger.info("Watching for changes...")
        event_handler = DevEventHandler(
            folder=abs_folder,
            debounce_seconds=debounce / 1000,
            symlinks=detect_symlink_support(),
        )
        observer = Observer()
        observer.schedule(
            event_handler, os.path.join(abs_folder, "src", "public"), recursive=True
        )
        observer.daemon = True
        observer.start()
        while True:
            time.sleep(0.1)
            if not server_thread.is_alive():
                break
            if not observer.is_alive():
                logger.warning("Observer stopped unexpectedly. Shutting down server...")
                server.shutdown()
                break
            event_handler.rebuild_if_appropriate()
        logger.info("Server stopped")
        if observer.is_alive():
            observer.stop()
            observer.join()
            logger.info("Observer stopped")
    finally:
        os.chdir(abs_cwd)


class DevEventHandler(FileSystemEventHandler):
    """Handles file system events from watchdog; when we receive an event
    we will perform a hot incremental rebuild. This will debounce the changes
    for some period of time, so that if many files are being changed at once
    (such as when doing a big find and replace), we only rebuild once.
    """

    def __init__(self, folder: str, debounce_seconds: float, symlinks: bool) -> None:
        self.folder = folder
        """Project root folder, an absolute path"""

        self.debounce_seconds = debounce_seconds
        """Minimum time before a rebuild in seconds"""

        self.symlinks = symlinks
        """Whether symlinks are supported"""

        self.lock = threading.RLock()
        """The lock for the deleted/changed/created/last_change_at variables."""

        self.deleted_files: Set[str] = set()
        self.changed_files: Set[str] = set()
        self.created_files: Set[str] = set()
        self.last_change_at = time.time()

    def rebuild_if_appropriate(self):
        """Rebuilds the project if it's appropriate to do so."""
        with self.lock:
            now = time.time()
            if (
                not self.deleted_files
                and not self.changed_files
                and not self.created_files
            ):
                return
            if now - self.last_change_at < self.debounce_seconds:
                return

            deleted = self.deleted_files.copy()
            changed = self.changed_files.copy()
            created = self.created_files.copy()

            self.deleted_files.clear()
            self.changed_files.clear()
            self.created_files.clear()

        logger.info("Rebuilding...")

        context = BuildContext(self.folder, dev=True, symlinks=self.symlinks)

        with open(context.config_file) as f:
            config = json.load(f)

        context.host = config["host"]

        old_dependency_graph = FileDependencyGraph()
        old_output_graph = FileDependencyGraph()

        if os.path.exists(context.dependency_graph_file):
            with open(context.dependency_graph_file) as f:
                old_dependency_graph = FileDependencyGraph.load(f)

        if os.path.exists(context.output_graph_file):
            with open(context.output_graph_file) as f:
                old_output_graph = FileDependencyGraph.load(f)

        changed_files = dict(
            (os.path.relpath(file, self.folder), get_file_signature(file))
            for file in changed
        )

        added_files = dict(
            (os.path.relpath(file, self.folder), get_file_signature(file))
            for file in created
        )

        deleted_files = list(os.path.relpath(file, self.folder) for file in deleted)

        if changed_files:
            for file, signature in changed_files.items():
                logger.debug(f"{file} changed: {signature}")

        if added_files:
            for file, signature in added_files.items():
                logger.debug(f"{file} added: {signature}")

        if deleted_files:
            for file in deleted_files:
                logger.debug(f"{file} deleted")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            hot_incremental_rebuild(
                context,
                old_dependency_graph,
                old_output_graph,
                changed_files,
                added_files,
                deleted_files,
            )
        )

        pending = asyncio.all_tasks(loop)
        while pending:
            loop.run_until_complete(
                asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
            )
            pending = asyncio.all_tasks(loop)

        asyncio.set_event_loop(None)
        loop.close()

    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        with self.lock:
            if event.src_path not in self.created_files:
                self.changed_files.add(event.src_path)
            self.last_change_at = time.time()

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        with self.lock:
            if event.src_path in self.deleted_files:
                self.deleted_files.remove(event.src_path)
                self.changed_files.add(event.src_path)
            else:
                self.created_files.add(event.src_path)
            self.last_change_at = time.time()

    def on_deleted(self, event: FileDeletedEvent):
        if event.is_directory:
            return
        with self.lock:
            if event.src_path in self.changed_files:
                self.changed_files.remove(event.src_path)
                self.deleted_files.add(event.src_path)
            elif event.src_path in self.created_files:
                self.created_files.remove(event.src_path)
            else:
                self.deleted_files.add(event.src_path)
            self.last_change_at = time.time()

    def on_moved(self, event: FileMovedEvent):
        if event.is_directory:
            return
        with self.lock:
            self.on_deleted(FileDeletedEvent(event.src_path))
            self.on_created(FileCreatedEvent(event.dest_path))
