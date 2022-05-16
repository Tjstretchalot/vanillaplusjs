from typing import Any, Dict, List, Literal, Optional, Pattern, Set, Tuple
from dataclasses import dataclass
from vanillaplusjs.build.build_file_result import BuildFileResult
import vanillaplusjs.build.html.token as tkn
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.html.manipulator import HTMLManipulator
from vanillaplusjs.build.scan_file_result import ScanFileResult
from vanillaplusjs.build.html.tokenizer import tokenize
import re
import json
import os


PREPROCESSOR_TEMPLATE_ACTION_RULE = re.compile(
    r"^\s*\[\s*TEMPLATE\s*:\s+(?P<args>.*)\]\s*$", flags=re.DOTALL
)
"""Regex that matches [TEMPLATE: <args>]. Allows newlines in args"""

PREPROCESSOR_STACK_ACTION_RULE = re.compile(r"^\s*\[\s*STACK\s*:\s+(?P<args>.*)\]\s*$")
"""Regex that matches [STACK: <args>]"""


class TemplateManipulator(HTMLManipulator):
    """Provides support for very basic templating. In particular, this allows
    creating a stack of variables, pushing/popping to/from the stack, and
    retrieving values from the stack as raw html Characters. Furthermore,
    this also supports the more commonly used [TEMPLATE: <path> <variables>]
    which will push to the stack, define the given variables, then load the
    given path as html and inject those values as tokens, then pop from the
    stack.

    The syntax is as follows:

        STACK PUSH: <!--[STACK: ["push", "<path>"]]-->
        STACK POP: <!--[STACK: ["pop"]]-->
        STACK DEFINE: <!--[STACK: ["define", "<key>", "<value>"]-->
        STACK RETRIEVE: <!--[STACK: ["retrieve", "<key>"]-->

        TEMPLATE: <!--[TEMPLATE: ["<path>", {"<key>": "<value>"}]]-->

    The paths for stack push or template should either start with a slash, which
    means relative to the src/partials folder, or be relative to the file being
    processed. The file being processed was either the original file we started
    with (if no stack was pushed), or the file that was last pushed to the stack.
    """

    def __init__(
        self, context: BuildContext, relpath: str, mode: Literal["scan", "build"]
    ) -> None:
        self.context = context
        self.relpath = relpath
        self.mode = mode

        self.dependencies: Optional[Set[str]] = set() if mode == "scan" else None
        self.produces: Optional[Set[str]] = set() if mode == "scan" else None

        self.children: Optional[Set[str]] = set() if mode == "build" else None
        self.produced: Optional[Set[str]] = set() if mode == "build" else None
        self.reused: Optional[Set[str]] = set() if mode == "build" else None

        self.stack: List[StackFrame] = []
        self.current_frame: StackFrame = StackFrame(
            relpath=self.relpath, variables=dict()
        )

    def start_mark(self, node: tkn.HTMLToken) -> bool:
        stack_command = self.try_get_command(PREPROCESSOR_STACK_ACTION_RULE, node)
        if stack_command is not None:
            return True

        template_command = self.try_get_command(PREPROCESSOR_TEMPLATE_ACTION_RULE, node)
        if template_command is not None:
            return True

        return False

    def continue_mark(self, node: tkn.HTMLToken) -> Optional[List[tkn.HTMLToken]]:
        stack_command = self.try_get_command(PREPROCESSOR_STACK_ACTION_RULE, node)
        if stack_command is not None:
            return self.handle_stack_command(stack_command)

        template_command = self.try_get_command(PREPROCESSOR_TEMPLATE_ACTION_RULE, node)
        if template_command is not None:
            return self.handle_template_command(template_command)

        return []

    def handle_stack_command(self, parsed_args: list) -> List[tkn.HTMLToken]:
        if self.is_stack_push(parsed_args):
            return self.handle_stack_push(parsed_args)

        if self.is_stack_pop(parsed_args):
            return self.handle_stack_pop()

        if cmd := self.try_get_stack_define(parsed_args):
            return self.handle_stack_define(*cmd)

        if cmd := self.try_get_stack_retrieve(parsed_args):
            return self.handle_stack_retrieve(cmd)

        return []

    def handle_stack_push(self, parsed_args: list) -> List[tkn.HTMLToken]:
        self.stack.append(self.current_frame)
        self.current_frame = StackFrame(relpath=parsed_args[1], variables=dict())
        return []

    def handle_stack_pop(self) -> List[tkn.HTMLToken]:
        assert self.stack, "Stack is empty"
        self.current_frame = self.stack.pop()
        return []

    def handle_stack_define(self, key: str, val: Any) -> List[tkn.HTMLToken]:
        self.current_frame.variables[key] = val
        return []

    def handle_stack_retrieve(self, key: str) -> List[tkn.HTMLToken]:
        assert key in self.current_frame.variables, f"{key} is not defined"
        assert isinstance(
            self.current_frame.variables[key], (str, int, float)
        ), f"{key} is not trivially retrievable"
        as_raw_text = str(self.current_frame.variables[key])
        return [tkn.HTMLToken(type="Characters", data=as_raw_text)]

    def handle_template_command(self, parsed_args: list) -> List[tkn.HTMLToken]:
        if imp := self.try_get_template_import(parsed_args):
            return self.handle_template_import(imp)

        return []

    def handle_template_import(self, imp: "TemplateImport") -> List[tkn.HTMLToken]:
        if self.mode == "scan":
            self.dependencies.add(imp.relpath)
        else:
            self.children.add(imp.relpath)

        result = []
        result.append(
            tkn.HTMLToken(
                type="Comment", data=f"[STACK: {json.dumps(['push', imp.relpath])}]"
            )
        )
        for key, val in imp.variables.items():
            result.append(
                tkn.HTMLToken(
                    type="Comment", data=f"[STACK: {json.dumps(['define', key, val])}]"
                )
            )
        with open(os.path.join(self.context.folder, imp.relpath), "r") as f:
            tokens = list(tokenize(f, fragment=True))
            result.extend(tokens)
        result.append(
            tkn.HTMLToken(type="Comment", data=f"[STACK: {json.dumps(['pop'])}]")
        )
        return result

    def is_stack_push(self, parsed_args: list) -> bool:
        return (
            parsed_args[0] == "push"
            and len(parsed_args) > 1
            and isinstance(parsed_args[1], str)
        )

    def is_stack_pop(self, parsed_args: list) -> bool:
        return parsed_args[0] == "pop"

    def try_get_stack_define(self, parsed_args: list) -> Optional[Tuple[str, Any]]:
        if parsed_args[0] != "define":
            return None

        if len(parsed_args) != 3:
            return None

        if not isinstance(parsed_args[1], str):
            return None

        return parsed_args[1], parsed_args[2]

    def try_get_stack_retrieve(self, parsed_args: list) -> Optional[str]:
        if parsed_args[0] != "retrieve":
            return None

        if len(parsed_args) != 2:
            return None

        if not isinstance(parsed_args[1], str):
            return None

        return parsed_args[1]

    def try_get_template_import(self, parsed_args: list) -> Optional["TemplateImport"]:
        if len(parsed_args) < 1:
            return None

        if not isinstance(parsed_args[0], str):
            return None

        command_path = parsed_args[0]
        variables = dict()

        if len(parsed_args) > 1:
            if not isinstance(parsed_args[1], dict):
                return None

            variables = parsed_args[1]

        if command_path.startswith("/"):
            # assume relative to src/partials
            command_path_rel_partials = command_path[1:].replace("/", os.path.sep)
            command_path_rel_project_root = os.path.join(
                "src", "partials", command_path_rel_partials
            )
        else:
            command_path_rel_current_relpath = command_path.replace("/", os.path.sep)
            command_path_rel_project_root = os.path.join(
                self.current_frame.relpath, command_path_rel_current_relpath
            )

        for var_key in list(variables.keys()):
            var_val = variables[var_key]
            if (
                isinstance(var_val, dict)
                and var_val.get("type") == "variable"
                and isinstance(var_val.get("name"), str)
            ):
                desired_variable_name = var_val.get("name")
                if desired_variable_name in self.current_frame.variables:
                    variables[var_key] = self.current_frame.variables[
                        desired_variable_name
                    ]

        return TemplateImport(
            relpath=command_path_rel_project_root, variables=variables
        )

    def try_get_command(
        self, regex: Pattern[str], node: tkn.HTMLToken
    ) -> Optional[List]:
        if node["type"] != "Comment":
            return None

        match = regex.match(node["data"])
        if match is None:
            return None

        match_args = match.group("args")
        try:
            parsed_args = json.loads(match_args)
        except json.JSONDecodeError:
            return None

        if not isinstance(parsed_args, list):
            return None

        if len(parsed_args) < 1:
            return None

        if not isinstance(parsed_args[0], str):
            return None

        return parsed_args

    def scan_result(self) -> ScanFileResult:
        assert not self.stack, "stack should be empty"
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        assert not self.stack, "stack should be empty"
        return BuildFileResult(
            children=list(self.children),
            produced=list(self.produced),
            reused=list(self.reused),
        )


@dataclass
class StackFrame:
    """Describes the current stack frame for the template processor,
    used to resolve variables in the template.
    """

    relpath: str
    """The file path relative to the project root containing the source
    code of this frame
    """

    variables: Dict[str, Any]
    """The variables defined in this stack frame"""


@dataclass
class TemplateImport:
    """Describes the arguments when importing a template."""

    relpath: str
    """The path to the file to import relative to the project root directory"""

    variables: Dict[str, Any]
    """The variables to pass to the imported template"""
