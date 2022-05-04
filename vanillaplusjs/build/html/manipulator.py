from typing import List, Optional
from vanillaplusjs.build.html.token import HTMLToken


class HTMLManipulator:
    """Describes something which is capable of manipulating HTML in a
    structured way.

    The manipulator will walk the node list of the parent document,
    and upon encountering a node may choose to mark it. After marking
    the node, the manipulator may eventually finish its mark, returning
    the nodes which should replace the nodes from the start to the end
    of the mark (inclusive).

    After replacing the nodes, the manipulator will start walking from
    the start of the returned nodes.
    """

    def start_mark(self, node: HTMLToken) -> bool:
        """Called if the manipulator does not have an active mark. If this
        returns true, the node is marked and this will call continue_mark
        with the given node next. If this returns false, the node is not
        marked and this will be called with the next node (if there is a next
        node)

        Args:
            node (HTMLToken): The node to potentially mark

        Returns:
            bool: True to mark the node, false to continue without marking
        """
        return False

    def continue_mark(self, node: HTMLToken) -> Optional[List[HTMLToken]]:
        """Called if the manipulator has an active mark. If this returns None,
        the mark remains and this will be called with the next node (if there
        are more nodes). If this returns a list, then the mark is completed,
        the nodes from the start to end of the mark (inclusive) are removed
        from the output, and the returned nodes are inserted instead. Then
        start_mark will be called with the first returned node, if any are
        returned, otherwise the next node in the sequence.

        Args:
            node (HTMLToken): The next marked node

        Returns:
            (list[HTMLToken], None): Either None, to continue the mark, or a
                list of nodes to replace the marked nodes with.
        """
        return []
