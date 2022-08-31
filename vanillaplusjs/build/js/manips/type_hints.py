from typing import Generator, List, Literal, Union
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.js.serializer import serialize_many
from vanillaplusjs.build.js.token import JSToken, JSTokenType
from vanillaplusjs.build.js.yield_manipulator import JSYieldManipulator
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.scan_file_result import ScanFileResult


class TypeHintsManipulator(JSYieldManipulator):
    """If a line contains a comment which, when stripped, looks like
    @@type-hint, then the entire line is commented out. This is useful for type
    hints which need to be in the code for the IDE to pick them up, but which
    do not constitute valid javascript. The most prominent case is when overloading
    function definitions for type hints, hence the name of this manipulator.
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        super().__init__()
        self.context = context
        self.relpath = relpath
        self.mode = mode

        self._skip_next_line = False

    def handle(
        self, token: JSToken
    ) -> Generator[None, JSToken, Union[Literal[False], List[JSToken]]]:
        if self.mode == "scan":
            return False

        if self._skip_next_line:
            self._skip_next_line = token["type"] != JSTokenType.line_terminator
            return False

        should_exclude_line = False
        while token["type"] not in (JSTokenType.line_terminator, JSTokenType.eof):
            if (
                not should_exclude_line
                and token["type"] == JSTokenType.comment
                and token["value"].strip() == "@@type-hint"
            ):
                should_exclude_line = True

            token = yield

        if not should_exclude_line:
            self._skip_next_line = True
            return False

        return [
            JSToken(type=JSTokenType.comment, value=serialize_many(self.stack[:-1])),
            self.stack[-1],
        ]

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=[], produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=[], produced=[], reused=[])
