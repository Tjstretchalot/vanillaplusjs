from typing import Generator, List, Optional, Literal, Union
from vanillaplusjs.build.js.manipulator import JSManipulator
from .token import JSToken, JSTokenType
import abc


class JSYieldManipulator(abc.ABC, JSManipulator):
    """An abstract base class for a javascript manipulator which operates
    on sequences of tokens rather than a single token. This can be done with
    a state machine, but it's much easier to do in pseudo-linear fashion by
    means of generator.

    The implementing class only has one function to implement - handle - which
    is called on each token. If the function returns False without yielding,
    then it's exactly like returning False from start_mark.

    If the function returns a list of nodes without yielding, it's as if it
    returned True from start_mark, and then that list of nodes from
    continue_mark.

    If the function yields, it immediately implies that a mark was started,
    and we send the function the next token (skipping one call to continue_mark).
    Eventually the function must return either the value `False` or
    a list of JSTokens to replace. In the `False` case we return from `continue_mark`
    the nodes as they were. Otherwise, we return the specified nodes.

    Thus, removing whitespace which is followed by a comment could be done with:

    ```py
    def handle(self, token: JSToken) -> Generator[None, JSToken, Union[Literal[False], List[JSToken]]]:
        if token['type'] != JSTokenType.whitespace:
            return False
        token = yield
        if token['type'] != JSTokenType.comment:
            return False
        return [token]
    ```

    Note that the generator will never be resumed if it yields after the eof
    token, so we will detect this case and raise an error.
    """

    def __init__(self) -> None:
        super().__init__()
        self.state: Literal["unmarked", "replacing", "skipping", "marking"] = "unmarked"
        """unmarked: We expect to get a start_mark call
        replacing: We are marked; on the next continue_mark call, return the stack
        skipping: We are marked; on the next continue_mark call, return None and set
          the state to marking
        marking: We are marked; on the next continue_mark call, send to the generator
        """

        self.stack: Optional[List[JSToken]] = None
        self.generator: Optional[
            Generator[None, JSToken, Union[Literal[False], List[JSToken]]]
        ] = None

    def start_mark(self, node: JSToken) -> bool:
        assert self.state == "unmarked", "start_mark called when already marked"

        generator = self.handle(node)
        try:
            next(generator)
            if node["type"] == JSTokenType.eof:
                raise RuntimeError(f"{self.__class__}.handle yielded on EOF")

            self.state = "skipping"
            self.stack = [node]
            self.generator = generator
            return True
        except StopIteration as e:
            if e.value is False:
                return False

            if not isinstance(e.value, (list, tuple)):
                raise TypeError(
                    f"handle must return a list or False, not {type(e.value)} ({e.value=})"
                )

            self.state = "replacing"
            self.stack = e.value
            return True

    def continue_mark(self, node: JSToken) -> Optional[List[JSToken]]:
        assert self.state in (
            "replacing",
            "skipping",
            "marking",
        ), "continue_mark called when not marked"
        if self.state == "replacing":
            res = self.stack
            self.state = "unmarked"
            self.stack = None
            return res

        if self.state == "skipping":
            self.state = "marking"
            return None

        self.stack.append(node)
        try:
            self.generator.send(node)
            if node["type"] == JSTokenType.eof:
                raise RuntimeError(f"{self.__class__}.handle yielded on EOF")
            return None
        except StopIteration as e:
            if e.value is False:
                res = self.stack
                self.state = "unmarked"
                self.stack = None
                self.generator = None
                return res

            if not isinstance(e.value, (list, tuple)):
                raise TypeError(
                    f"handle must return a list or False, not {type(e.value)} ({e.value=})"
                )

            self.state = "unmarked"
            self.stack = None
            self.generator = None
            return e.value

    @abc.abstractmethod
    def handle(
        self, node: JSToken
    ) -> Generator[None, JSToken, Union[Literal[False], List[JSToken]]]:
        """See class-level docs.

        This is the only function required by subclasses. Will be called
        once per node. If it returns False, then the node is not modified.
        Otherwise, it must return a list of nodes to replace the nodes that
        were sent to it (including the node itself). Yield result is ignored,
        sent the next node.
        """
        raise NotImplementedError("not implemented")
