from typing import List, Optional
from .manipulator import HTMLManipulator
from .token import HTMLToken


class HTMLBuilder(HTMLManipulator):
    """Produces a sequence of tokens from a list of tokens and a list of
    manipulators.
    """

    def __init__(self, manipulators: List[HTMLManipulator]):
        self.output: List[HTMLToken] = []
        """The unconsumed output tokens, i.e., tokens which we have already
        produced but haven't yet been requested via available_tokens
        """

        self.manipulators = manipulators
        """The manipulators for the current tokens.
        """

        self.mark: Optional[HTMLManipulator] = None
        """If an HTMLManipulator is currently marked, consuming tokens, then
        the HTMLManipulator which is currently marked.
        """

    def consume_tokens(self) -> List[HTMLToken]:
        """Returns any unconsumed output tokens and consumes them. This can be
        used to reduce the memory usage of this file for long streams, though
        in the simplest case you can just stream all the tokens to this builder
        via handle_token and then, once done, call consume_tokens to get the
        output.
        """
        output = self.output
        self.output = []
        return output

    def handle_token(self, token: HTMLToken) -> None:
        """Handles the next token in the stream. It is possible that output
        tokens that result from this token are delayed, i.e., are not determined
        until a later call.
        """
        stack = [token]
        while stack:
            token = stack.pop(0)
            if self.mark is None:
                for manipulator in self.manipulators:
                    if manipulator.start_mark(token):
                        self.mark = manipulator
                        break

                if self.mark is None:
                    self.output.append(token)
                    continue

            replacement_tokens = self.mark.continue_mark(token)
            if replacement_tokens is not None:
                stack = replacement_tokens + stack
                self.mark = None
