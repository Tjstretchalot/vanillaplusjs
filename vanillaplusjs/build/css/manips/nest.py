from multiprocessing.sharedctypes import Value
from xml.etree.ElementTree import Comment
from vanillaplusjs.build.css.manipulator import CSSManipulator
from typing import Dict, List, Literal, Optional, Set, Generator
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file import BuildFileResult
from vanillaplusjs.build.css.tokenizer import tokenize_and_close
from vanillaplusjs.build.scan_file import ScanFileResult
from vanillaplusjs.build.css.token import CSSToken, CSSTokenType
import vanillaplusjs.build.css.serializer
from dataclasses import dataclass
import re
import os
from loguru import logger


@dataclass
class QualifiedRule:
    """Describes a qualified rule, which is a prelude followed by a simple
    block. https://www.w3.org/TR/css-syntax-3/#consume-a-qualified-rule
    """

    tokenized_prelude: List[CSSToken]
    """The prelude as a list of tokens"""

    serialized_prelude: str
    """The prelude as a string"""

    simple_block: List[CSSToken]
    """The simple block as a list of tokens. This starts from the
    first node after the left curly brace, and ends on the last node
    before the right curly brace.
    """


@dataclass(frozen=True)
class QualifiedRuleReference:
    """A reference to a qualified rule in a stylesheet."""

    relpath: str
    """The relative path to the stylesheet expected to contain the rule"""

    prelude: str
    """The expected stripped prelude for the qualified rule"""


@dataclass
class UnresolvedQualifiedRule:
    """Describes an unresolved qualified rule"""

    rule: QualifiedRule
    """The rule, which still includes tokens which have not been resolved"""

    missing_references: Set[QualifiedRuleReference]
    """The references which are required to resolve the rule"""


@dataclass
class ReferencableRules:
    """Describes rules which can be referenced by other rules or are as
    yet unresolved.
    """

    processed_files: Set[str]
    """The files which have been processed"""

    available_rules: Dict[QualifiedRuleReference, QualifiedRule]
    """Rules which are completely resolved"""

    unresolved_rules: Dict[QualifiedRuleReference, UnresolvedQualifiedRule]
    """Rules which have not been resolved yet because they are waiting on
    other rules to resolvs. The keys list is unique and the values list
    is unique.

    Note that rules may be in this list because when we first encountered
    them we could not resolve them, we have now resolved all the missing
    references, but we have not yet resolved the rule. Such rules are
    maintained in the `resolvable_rules` set.
    """

    missing_references_to_unresolved_rules: Dict[
        QualifiedRuleReference, List[QualifiedRuleReference]
    ]
    """Maps from missing references to the rules that were waiting
    on that reference. Unresolved rules may be waiting on multiple
    references, but this allows us to know immediately what rules
    might be ready to process after we encounter a qualified rule.
    """

    relpaths_to_missing_references_count: Dict[str, int]
    """Maps from a relative path for an import to the number of
    missing references from that relpath. This should be identical
    to the result of

    ```py
    res = dict()
    for unresolved_rule in unresolved_rules.values():
        for missing_reference in unresolved_rule.missing_references:
            res[missing_reference.relpath] = res.get(missing_reference.relpath, 0) + 1
    ```

    This is intended to let us know when we can stop processing a
    stylesheet, even when we haven't reached the end yet, because
    we have no more missing references to that stylesheet.

    This will not have any values which are 0 or lower; keys should be removed
    from the dict if there are no missing references, so that
    relpaths_to_missing_references_count.keys() consists of all the relative
    that still need to be processed in order to resolve the rules we have
    already seen.
    """

    resolvable_rules: Set[QualifiedRuleReference]
    """A set of rules which are currently in unresolved_rules but have no
    missing references.
    """

    def set_rule(
        self,
        relpath: str,
        prelude: str,
        rule: QualifiedRule,
        missing_references: Optional[Set[QualifiedRuleReference]] = None,
    ) -> None:
        """Convenience function to add the given rule to the list and update
        all the necessary data structures. If the rule has no missing references
        it will be added to the available_rules dict. If it has missing references
        it will be added to the unresolved_rules dict.

        If the rule already exists it is updated. You may add or removing missing
        references to an existing rule, so long as the rule is not available. Once
        a rule is available then attempting to set it again will raise ValueError.

        Args:
            relpath: The relative path to the stylesheet that contains the rule
            prelude: The stripped prelude for the rule
            rule: The rule to add
            missing_references: The missing references for resolving the rule

        Raises:
            ValueError: If the rule is already available
        """
        ref = QualifiedRuleReference(relpath=relpath, prelude=prelude)
        if ref in self.available_rules:
            raise ValueError(f"Rule {ref} is already available")
        logger.debug(
            "set_rule({}, {}, missing_references={})",
            relpath,
            prelude,
            missing_references,
        )
        if not missing_references:
            self.unresolved_rules.pop(ref, None)
            self.resolvable_rules.discard(ref)
            self.available_rules[ref] = rule

            waiting_rules = self.missing_references_to_unresolved_rules.pop(ref, None)
            if waiting_rules is None:
                waiting_rules = []
            else:
                self.relpaths_to_missing_references_count[relpath] -= 1
                if self.relpaths_to_missing_references_count[relpath] == 0:
                    self.relpaths_to_missing_references_count.pop(relpath)

            for waiting_rule_ref in waiting_rules:
                unresolved_rule = self.unresolved_rules[waiting_rule_ref]
                unresolved_rule.missing_references.remove(ref)
                if not unresolved_rule.missing_references:
                    self.resolvable_rules.add(waiting_rule_ref)

            return

        old_unresolved_rule = self.unresolved_rules.pop(
            ref, UnresolvedQualifiedRule(rule=rule, missing_references=set())
        )
        unresolved_rule = UnresolvedQualifiedRule(
            rule=rule, missing_references=missing_references
        )
        self.unresolved_rules[ref] = unresolved_rule

        for missing_reference in (
            missing_references - old_unresolved_rule.missing_references
        ):
            unresolved_list = self.missing_references_to_unresolved_rules.get(
                missing_reference
            )
            if unresolved_list is None:
                unresolved_list = []
                self.missing_references_to_unresolved_rules[
                    missing_reference
                ] = unresolved_list
            unresolved_list.append(ref)

            self.relpaths_to_missing_references_count[missing_reference.relpath] = (
                self.relpaths_to_missing_references_count.get(
                    missing_reference.relpath, 0
                )
                + 1
            )

        for missing_reference in (
            old_unresolved_rule.missing_references - missing_references
        ):
            unresolved_list = self.missing_references_to_unresolved_rules[
                missing_reference
            ]
            unresolved_list.remove(ref)
            if not unresolved_list:
                self.missing_references_to_unresolved_rules.pop(missing_reference)
                self.relpaths_to_missing_references_count[
                    missing_reference.relpath
                ] -= 1
                if (
                    self.relpaths_to_missing_references_count[missing_reference.relpath]
                    == 0
                ):
                    self.relpaths_to_missing_references_count.pop(
                        missing_reference.relpath
                    )


# Regex that matches !PREPROCESSOR: import [args]
PREPROCESSOR_IMPORT_ACTION_RULE = re.compile(
    r"^\s*!\s*PREPROCESSOR\s*:\s+import\s+(?P<args>.*)\s*$"
)


class NestManipulator(CSSManipulator):
    """Allows simple CSS nesting via importing another style into a given
    style.

    For example,

    ```css
    .bg-white {
        background: white;
    }

    .button {
        padding: 12px;
        /*! PREPROCESSOR: import .bg-white */
    }
    ```

    If the import command is used as above, it will import the style from
    the default stylesheet for the project (typically src/public/css/main.css).
    If you want to import from a different stylesheet, you can specify a
    url relative to src/public like follows:

    ```css
    .button {
        padding: 12px;
        /*! PREPROCESSOR: import .unstyle FROM /css/unstyle.css */
    }
    ```

    The imports must not form circular dependencies, i.e., main.css importing
    unstyle.css importing main.css. However, it is possible to import from
    within a file before a style is defined, even when that style itself
    imports other styles --

    ```css
    .button {
        padding: 12px;
        /*! PREPROCESSOR: import .elevated-white */
    }

    .elevated-white {
        /*! PREPROCESSOR: import .bg-white */
        /*! PREPROCESSOR: import .box-shadow-large */
    }

    .bg-white {
        background: white;
    }

    .box-shadow-large {
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
    }
    ```

    Note that while the above examples illustrate the feature, for bg-white
    it would be better to use the standard css variables supported by the
    browser:

    ```
    :root {
        --col-white: #fff;
    }

    .button {
        background: var(--col-white);
    }
    ```

    Also note that while you can invert the order within a single file, it can
    be substantially faster to declare in the order they are needed. Furthermore,
    when importing styles from other stylesheets, it will typically be faster
    if the things you are importing are either in a small file or near the top
    of the file.
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
        self.produced: Optional[List[str]] = [] if mode == "build" else None
        self.reused: Optional[List[str]] = [] if mode == "build" else None

        self.referencable_rules: Optional[ReferencableRules] = (
            ReferencableRules(
                processed_files=set(),
                available_rules=dict(),
                unresolved_rules=dict(),
                missing_references_to_unresolved_rules=dict(),
                relpaths_to_missing_references_count=dict(),
                resolvable_rules=set(),
            )
            if mode == "build"
            else None
        )

        self.resumable_imports: Optional[Dict[str, Generator[CSSToken, None, None]]] = (
            dict() if mode == "build" else None
        )
        """We do not completely resolve other files when they are imported.
        Instead, we will keep going only until we have resolved the imports
        we need from that file. If we later encounter a rule that references
        a style from a file we started but did not finish resolving, we will
        resume importing from that file.
        """

    def start_mark(self, node: CSSToken) -> bool:
        if node["type"] == CSSTokenType.eof:
            if self.mode == "build":
                for gen in self.resumable_imports.values():
                    gen.close()
                self.resumable_imports = None
            return False

        imp = self._get_import(node)
        if imp is None:
            return
        if self.mode == "scan":
            if imp.relpath != self.relpath:
                self.dependencies.add(imp.relpath)
            return False

        if imp.relpath != self.relpath:
            self.children.add(imp.relpath)
        return True

    def _get_import(self, node: CSSToken) -> Optional[QualifiedRuleReference]:
        """Determines the qualified rule reference to import at the given node,
        if any.
        """
        if node["type"] != CSSTokenType.comment:
            return None

        match = PREPROCESSOR_IMPORT_ACTION_RULE.match(node["value"])
        if not match:
            return

        args = match.group("args")
        args = args.strip()
        try:
            from_index = args.lower().index("from")
        except ValueError:
            from_index = None

        import_relpath = None
        if from_index is not None:
            from_arg = args[from_index + 4 :].strip()
            if not from_arg.startswith("/") or " " in from_arg:
                # parse error
                return

            path_relative_to_public = from_arg[1:].replace("/", os.path.sep)
            path_relative_to_root = os.path.join(
                "src", "public", path_relative_to_public
            )
            import_relpath = path_relative_to_root
        else:
            import_relpath = self.context.default_css_file.replace("/", os.path.sep)

        import_prelude = (
            args.strip() if from_index is None else args[:from_index].strip()
        )
        return QualifiedRuleReference(import_relpath, import_prelude)

    def continue_mark(self, node: CSSToken) -> Optional[List[CSSToken]]:
        imp = self._get_import(node)
        assert imp is not None, "continuing mark on non-import node"

        self._ensure_resolved(imp)
        return self.referencable_rules.available_rules[imp].simple_block

    def _ensure_resolved(self, imp: QualifiedRuleReference) -> None:
        """Does whatever is necessary to resolve the given import, if it
        is possible to do so.
        """
        logger.debug("resolving import {} in {}", repr(imp), self.relpath)

        self._resolve_resolvable()
        if imp in self.referencable_rules.available_rules:
            return

        if imp.relpath != self.relpath:
            return self._ensure_child_import_resolved(imp)

        return self._ensure_local_import_resolved(imp)

    def _ensure_child_import_resolved(self, imp: QualifiedRuleReference) -> None:
        """Ensures that a child import is resolved, i.e., an import from a different
        file. We don't need to do most of the work to resolve this import; we
        know that we have marked imp.relpath as a child of this file, meaning
        that it must have been resolved prior to us starting to resolve this
        file. Meaning that we can use the output of that file to resolve this
        import, saving us a lot of time.
        """

        path_relative_to_public = imp.relpath[
            len(os.path.join("src", "public")) + len(os.path.sep) :
        ]
        out_path_relative_to_root = os.path.join("out", "www", path_relative_to_public)

        generator = self.resumable_imports.get(out_path_relative_to_root)
        if generator is None:
            if out_path_relative_to_root in self.resumable_imports:
                raise ValueError(
                    f"cannot resolve {imp} because we exhausted it before finding {imp.prelude}"
                )
            generator = tokenize_and_close(
                open(os.path.join(self.context.folder, out_path_relative_to_root))
            )
            self.resumable_imports[out_path_relative_to_root] = generator
        self._ensure_import_resolved_using(imp, generator)

    def _ensure_local_import_resolved(self, imp: QualifiedRuleReference) -> None:
        """Ensures that the given local import is resolved. Unlike with
        child imports, this is going to use the raw values in the file, meaning
        that other manipulators will have to redo any work they did to process
        that import every time it's imported. This is a performance penalty but
        can be an upside if the other manipulators are context-sensitive.
        """
        generator = self.resumable_imports.get(self.relpath)
        if generator is None:
            if self.relpath in self.resumable_imports:
                raise ValueError(
                    f"cannot resolve {imp} because we exhausted it before finding {imp.prelude}"
                )
            generator = tokenize_and_close(
                open(os.path.join(self.context.folder, self.relpath))
            )
            self.resumable_imports[self.relpath] = generator

        self._ensure_import_resolved_using(imp, generator)

    def _ensure_import_resolved_using(
        self, imp: QualifiedRuleReference, generator: Generator[CSSToken, None, None]
    ) -> None:
        # The generator will always be resumed at the top-level, i.e., not nested in an
        # at rule or something like that.

        # https://www.w3.org/TR/css-syntax-3/#parser-diagrams serves as a basic for
        # allowed parsing. In other words, we're guarranteed to encounter a stylesheet,
        # assuming the css file is valid.

        while True:
            self._resolve_resolvable()
            if imp in self.referencable_rules.available_rules:
                return

            token = next(generator)
            if token["type"] == CSSTokenType.eof:
                raise ValueError(f"{imp=}")

            if token["type"] == CSSTokenType.cdo:
                while token["type"] != CSSTokenType.cdc:
                    token = next(generator)
                    if token["type"] == CSSTokenType.eof:
                        raise ValueError(f"{imp=}")
                continue

            if token["type"] == CSSTokenType.at_keyword:
                while token["type"] != CSSTokenType.left_curly_bracket:
                    token = next(generator)
                    if token["type"] == CSSTokenType.eof:
                        raise ValueError(f"{imp=}")
                nest_level = 1
                while nest_level > 0:
                    token = next(generator)
                    if token["type"] == CSSTokenType.eof:
                        raise ValueError(f"{imp=}")
                    if token["type"] == CSSTokenType.left_curly_bracket:
                        nest_level += 1
                    elif token["type"] == CSSTokenType.right_curly_bracket:
                        nest_level -= 1
                continue

            if token["type"] == CSSTokenType.whitespace:
                continue

            prelude: List[CSSToken] = [token]

            while True:
                token = next(generator)
                if token["type"] == CSSTokenType.eof:
                    raise ValueError(f"{imp=}")
                if token["type"] == CSSTokenType.left_curly_bracket:
                    break
                prelude.append(token)

            serialized_prelude = vanillaplusjs.build.css.serializer.serialize_many(
                prelude
            ).strip()
            logger.debug("encountered {} in {}", serialized_prelude, imp.relpath)

            stack: List[CSSToken] = []
            value: List[CSSToken] = []
            missing_references: Set[QualifiedRuleReference] = set()

            while True:
                token = stack.pop(0) if stack else next(generator)
                if not value and token["type"] == CSSTokenType.whitespace:
                    continue

                if (nested_import := self._get_import(token)) is not None:
                    if nested_import in self.referencable_rules.available_rules:
                        stack = (
                            self.referencable_rules.available_rules[
                                nested_import
                            ].simple_block
                            + stack
                        )
                    else:
                        missing_references.add(nested_import)
                        value.append(token)
                    continue

                if token["type"] == CSSTokenType.eof:
                    raise ValueError(f"{imp=}")

                if token["type"] == CSSTokenType.left_curly_bracket:
                    # parse error, maybe something else will clean it up
                    value.append(token)
                    nest_level = 1
                    while nest_level > 0:
                        token = next(generator)
                        if token["type"] == CSSTokenType.eof:
                            raise ValueError(f"{imp=}")
                        value.append(token)
                        if token["type"] == CSSTokenType.left_curly_bracket:
                            nest_level += 1
                        elif token["type"] == CSSTokenType.right_curly_bracket:
                            nest_level -= 1
                    continue

                if token["type"] == CSSTokenType.right_curly_bracket:
                    break

                value.append(token)

            while value and value[-1]["type"] == CSSTokenType.whitespace:
                value.pop()

            self.referencable_rules.set_rule(
                imp.relpath,
                serialized_prelude,
                QualifiedRule(
                    tokenized_prelude=prelude,
                    serialized_prelude=serialized_prelude,
                    simple_block=value,
                ),
                missing_references=missing_references,
            )

    def _resolve_resolvable(self) -> None:
        """Resolves any imports which are ready to be resolved"""
        while self.referencable_rules.resolvable_rules:
            rule = next(iter(self.referencable_rules.resolvable_rules))

            self._resolve(rule)

    def _resolve(self, rule: QualifiedRuleReference) -> None:
        """Resolves the given rule."""
        logger.debug("resolving {}", repr(rule))
        unresolved_rule = self.referencable_rules.unresolved_rules[rule]
        new_nodes = []
        stack = list(unresolved_rule.rule.simple_block)
        while stack:
            node = stack.pop(0)
            imp = self._get_import(node)
            if imp is None:
                new_nodes.append(node)
                continue

            referenced_rule = self.referencable_rules.available_rules[imp]
            stack = referenced_rule.simple_block + stack

        resolved_rule = QualifiedRule(
            tokenized_prelude=unresolved_rule.rule.tokenized_prelude,
            serialized_prelude=unresolved_rule.rule.serialized_prelude,
            simple_block=new_nodes,
        )
        self.referencable_rules.set_rule(rule.relpath, rule.prelude, resolved_rule)

    def scan_result(self) -> ScanFileResult:
        """The scan result for this manipulator"""
        return ScanFileResult(
            dependencies=list(self.dependencies), produces=list(self.produces)
        )

    def build_result(self) -> BuildFileResult:
        """The build result for this manipulator."""
        return BuildFileResult(
            children=list(self.children), produced=self.produced, reused=self.reused
        )
