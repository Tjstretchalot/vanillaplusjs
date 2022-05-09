from typing import Generator, List, Literal, Optional, Set, Tuple, Union
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.js.yield_manipulator import JSYieldManipulator
from vanillaplusjs.build.js.token import JSToken, JSTokenType
from vanillaplusjs.build.scan_file import ScanFileResult
from vanillaplusjs.constants import PROCESSOR_VERSION
import os


WHITESPACE_OR_TERM = {JSTokenType.whitespace, JSTokenType.line_terminator}


class HashImportsManipulator(JSYieldManipulator):
    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        super().__init__()
        self.context = context
        self.relpath = relpath
        self.mode = mode

        self.dependencies: Optional[Set[str]] = set() if mode == "scan" else None
        self.children: Optional[Set[str]] = set() if mode == "build" else None

        self.skip_next_import = False

    def handle(
        self, token: JSToken
    ) -> Generator[None, JSToken, Union[Literal[False], List[JSToken]]]:
        if not self.skip_next_import and self._is_skip_import_mark(token):
            self.skip_next_import = True
            return False

        if token["type"] != JSTokenType.keyword_import:
            return False
        if self.skip_next_import:
            self.skip_next_import = False
            return False

        token = yield from self._skip_types(WHITESPACE_OR_TERM)
        if token["type"] == JSTokenType.string_literal:
            return self._handle_import(token["value"])

        expecting_from = False
        if token["type"] == JSTokenType.identifier:
            token = yield from self._skip_types(WHITESPACE_OR_TERM)
            if token["type"] == JSTokenType.keyword_as:
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
                if token["type"] != JSTokenType.identifier:
                    return self._mark_import_bad("expected alias for default export")
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
                if token["type"] == JSTokenType.comma:
                    token = yield from self._skip_types(WHITESPACE_OR_TERM)
                else:
                    expecting_from = True
            elif token["type"] == JSTokenType.comma:
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
            else:
                expecting_from = True

        if not expecting_from and token["type"] == JSTokenType.asterisk:
            token = yield from self._skip_types(WHITESPACE_OR_TERM)
            if token["type"] == JSTokenType.keyword_as:
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
                if token["type"] != JSTokenType.identifier:
                    return self._mark_import_bad("expected alias for asterisk")
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
                if token["type"] == JSTokenType.comma:
                    token = yield from self._skip_types(WHITESPACE_OR_TERM)
                else:
                    expecting_from = True
            elif token["type"] == JSTokenType.comma:
                token = yield from self._skip_types(WHITESPACE_OR_TERM)
            else:
                expecting_from = True

        if not expecting_from and token["type"] == JSTokenType.open_curly_bracket:
            token = yield from self._skip_types(WHITESPACE_OR_TERM)
            while token["type"] != JSTokenType.close_curly_bracket:
                if token["type"] == JSTokenType.identifier:
                    token = yield from self._skip_types(WHITESPACE_OR_TERM)
                    if token["type"] == JSTokenType.keyword_as:
                        token = yield from self._skip_types(WHITESPACE_OR_TERM)
                        if token["type"] != JSTokenType.identifier:
                            return self._mark_import_bad(
                                "expected alias for named export"
                            )
                        token = yield from self._skip_types(WHITESPACE_OR_TERM)
                        if token["type"] not in (
                            JSTokenType.comma,
                            JSTokenType.close_curly_bracket,
                        ):
                            return self._mark_import_bad(
                                "expected comma or close curly bracket"
                            )
                    if token["type"] == JSTokenType.comma:
                        token = yield from self._skip_types(WHITESPACE_OR_TERM)
                else:
                    return self._mark_import_bad("expected named export")
            expecting_from = True
            token = yield from self._skip_types(WHITESPACE_OR_TERM)

        if not expecting_from:
            return self._mark_import_bad("expected next import")

        if token["type"] != JSTokenType.keyword_from:
            return self._mark_import_bad("expected from")

        token = yield from self._skip_types(WHITESPACE_OR_TERM)
        if token["type"] != JSTokenType.string_literal:
            return self._mark_import_bad("expected string literal after from")

        return self._handle_import(token["value"])

    def _handle_import(self, import_path: str) -> Union[Literal[False], List[JSToken]]:
        if not any(import_path.startswith(prefix) for prefix in ("/", "./", "../")):
            return self._mark_import_bad("unexpected path format")
        if any(ch in import_path for ch in "?#"):
            return self._mark_import_bad("path contains invalid characters")

        if import_path.startswith("/"):
            rel_to_root = os.path.join(
                "src", "public", import_path[1:].replace("/", os.path.sep)
            )
        else:
            abs_import_path = os.path.abspath(
                os.path.join(
                    self.context.folder,
                    self.relpath,
                    import_path.replace("/", os.path.sep),
                )
            )
            rel_to_root = os.path.relpath(
                abs_import_path, os.path.abspath(self.context.folder)
            )

        if self.mode == "scan":
            self.dependencies.add(rel_to_root)
            self.skip_next_import = True
            return False

        self.children.add(rel_to_root)

        rel_to_public = os.path.relpath(rel_to_root, os.path.join("src", "public"))

        exp_hash_file = os.path.join(
            self.context.folder, "out", "www", rel_to_public + ".hash"
        )
        if not os.path.exists(exp_hash_file):
            raise FileNotFoundError(exp_hash_file)

        with open(exp_hash_file, "r") as f:
            file_hash = f.read()

        new_import_path = import_path + f"?v={file_hash}&pv={PROCESSOR_VERSION}"
        self.skip_next_import = True
        return self.stack[:-1] + [
            JSToken(type=JSTokenType.string_literal, value=new_import_path)
        ]

    def _skip_types(
        self, to_skip: Set[JSTokenType]
    ) -> Generator[None, JSToken, JSToken]:
        while True:
            token = yield
            if token["type"] not in to_skip:
                return token

    def _expect_sequence(
        self, exp: List[JSTokenType], ignore: Set[JSTokenType]
    ) -> Generator[None, JSToken, bool]:
        for exp_token in exp:
            act_token = yield from self._skip_types(ignore)
            if act_token["type"] != exp_token:
                return False
        return True

    def _expect_alias(
        self, token: Optional[JSToken] = None
    ) -> Generator[None, JSToken, bool]:
        if token is None:
            token = yield
        if token != JSTokenType.keyword_as:
            return False
        token = yield from self._skip_types(WHITESPACE_OR_TERM)
        if token["type"] != JSTokenType.identifier:
            return False
        return True

    def _mark_import_bad(self, hint="") -> List[JSToken]:
        return [
            JSToken(
                type=JSTokenType.comment,
                value=f"PREPROCESSOR: ignore-import {hint}; final token: {self.stack[-1]['type']}",
            )
        ] + self.stack

    def _is_skip_import_mark(self, token: JSToken) -> bool:
        return token["type"] == JSTokenType.comment and token["value"].startswith(
            "PREPROCESSOR: ignore-import"
        )

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator is always empty."""
        return ScanFileResult(dependencies=list(self.dependencies), produces=[])

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator is always empty."""
        return BuildFileResult(children=list(self.children), produced=[], reused=[])
