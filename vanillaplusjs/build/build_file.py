from dataclasses import dataclass
from typing import List
from .build_context import BuildContext


@dataclass
class BuildFileResult:
    """The result of building a file."""

    children: List[str]
    """The relative paths (to the project root) of the files we relied on to
    build this file. This must exactly match the scanned children of the file.
    """

    produced: List[str]
    """The relative paths (to the project root) of the files that were produced
    by this file.
    """

    reused: List[str]
    """The relative paths (to the project root) of the files which we would have
    produced, but they were already available, so we did not produce them.
    """


import vanillaplusjs.build.handlers.copy


def build_file(build_context: BuildContext, relpath: str) -> BuildFileResult:
    """Builds the file within the given context. This assumes that all the
    children have already been built. This MUST be multi-process safe; this MAY
    be called concurrently for different files.

    It is guarranteed that we will not concurrently build two files which
    produce the same outputs, unless those outputs have already been built.

    It is guarranteed that if an output will be built by this, if it already
    exists, it can be assumed that it will be the same as the output produced
    by this.

    Args:
        build_context (BuildContext): The configuration for the build

    Returns:
        BuildFileResult: If the file is built successfully
    """
    return vanillaplusjs.build.handlers.copy.build_file(build_context, relpath)
