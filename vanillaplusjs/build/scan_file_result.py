from typing import Dict, List, Optional
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

    placeholders: Optional[Dict[str, str]] = None
    """At scanning time we may decide to generate source files. This is typically
    used to complete placeholders that we recognize are missing, generally only
    behind a settings flag.

    If None, treated like an empty dictionary. The dictionary keys are file
    paths relative to the project root, and the values are the contents of the
    files that should be generated. If multiple scan results would like to
    create the same file, one of them will be chosen arbitrarily. The generated
    placeholder files will go through a scan and build flow as if they existed
    at the start of the build.
    """
