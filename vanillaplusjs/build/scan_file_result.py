from typing import List
from dataclasses import dataclass


@dataclass
class ScanFileResult:
    """Result of successfully scanning a file."""

    dependencies: List[str]
    """The files which must have been built before this file can be built"""

    produces: List[str]
    """The files which will be produced when building this file. We guarrantee
    repeatable rebuilds, meaning that it will produce the exact same set of
    files with the exact same contents every time. Furthermore, if two different
    files produce the same output file, then they will both produce the same
    output file.
    """
