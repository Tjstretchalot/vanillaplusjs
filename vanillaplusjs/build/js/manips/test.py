from typing import Generator, List, Literal, Union
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.js.yield_manipulator import JSYieldManipulator
from vanillaplusjs.build.js.token import JSToken, JSTokenType
from vanillaplusjs.build.scan_file import ScanFileResult


class TestManipulator(JSYieldManipulator):
    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        super().__init__()

    def handle(
        self, token: JSToken
    ) -> Generator[None, JSToken, Union[Literal[False], List[JSToken]]]:
        if token["type"] != JSTokenType.whitespace:
            return False
        token = yield
        if token["type"] != JSTokenType.comment:
            return False
        return [token]

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=[], produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=[], produced=[], reused=[])
