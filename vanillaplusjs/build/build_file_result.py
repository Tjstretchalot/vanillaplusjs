from dataclasses import dataclass
from typing import List


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
