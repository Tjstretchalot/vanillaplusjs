"""A thin wrapper around uvicorn - spawns a uvicorn server which
will serve files
"""
import contextlib
import threading
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
import time


@contextlib.contextmanager
def host_static_files(folder: str, host: str, port: int):
    """Starts a uvicorn server in a separate thread, yields None, and
    then shuts down the server.

    https://github.com/encode/uvicorn/discussions/1103
    """
    routes = [
        Mount("/", app=StaticFiles(directory=folder, html=True), name="static"),
    ]

    app = Starlette(routes=routes)

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config=config)

    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    try:
        while not server.started:
            time.sleep(1e-3)
        yield
    finally:
        server.should_exit = True
        thread.join()


def host_static_files_with_event(
    folder: str, host: str, port: int, event: threading.Event
):
    """Hosts static files in the given server via the given host and port
    until the given event is set.
    """
    with host_static_files(folder, host, port):
        event.wait()
