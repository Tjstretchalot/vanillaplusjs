from typing import Sequence
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from loguru import logger
import signal
import threading
import time
import sys


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(prog="vanillajsplus run", description="")
    argparser.add_argument(
        "--port", type=int, default=8888, help="The port to run the webserver on"
    )
    argparser.add_argument(
        "--host", type=str, default="localhost", help="The host to run the webserver on"
    )
    argparser.add_argument(
        "--folder",
        type=str,
        default=".",
        help="The folder containing vanillaplusjs.json",
    )
    args = argparser.parse_args(args)

    run_server(host=args.host, port=args.port, folder=args.folder)


def run_server(host: str, port: int, folder: str) -> None:
    if not os.path.exists(os.path.join(folder, "vanillaplusjs.json")):
        logger.warning(
            'vanillaplusjs.json not found. Call "vanillaplusjs init" to create it.'
        )
        sys.exit(1)

    if not os.path.exists(os.path.join(folder, "out", "www", "index.html")):
        logger.warning(
            'out/www/index.html not found. Call "vanillaplusjs build" to create it.'
        )
        sys.exit(1)

    abs_cwd = os.path.abspath(os.getcwd())
    os.chdir(os.path.join(folder, "out", "www"))
    try:
        logger.info(f"Running server on {host}:{port}")
        server = HTTPServer((host, port), SimpleHTTPRequestHandler)

        def handler(signal, frame):
            logger.info("Shutting down server...")
            server.shutdown()

        signal.signal(signal.SIGINT, handler)
        thread = threading.Thread(
            target=server.serve_forever, kwargs={"poll_interval": 0.1}
        )
        thread.daemon = True
        thread.start()
        while True:
            time.sleep(0.1)
            if not thread.is_alive():
                break
        logger.info("Server stopped")
    finally:
        os.chdir(abs_cwd)
