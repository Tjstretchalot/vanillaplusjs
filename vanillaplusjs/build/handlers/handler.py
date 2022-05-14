from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult


class Handler:
    """Describes something which acts as a handler. Typically
    a handler is not actually a subclass of this but rather a module
    with the same functions.
    """

    def scan_file(self, context: BuildContext, relpath: str) -> ScanFileResult:
        raise NotImplementedError()

    def build_file(self, context: BuildContext, relpath: str) -> BuildFileResult:
        raise NotImplementedError()
