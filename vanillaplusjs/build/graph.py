"""Stores the file dependencies via a modified adjacency list."""
from typing import Dict, List, Literal, Optional, Set, Tuple
import io
import json
from dataclasses import dataclass
from enum import Enum


class FileRelationship:
    """Describes a relationship between two files"""

    parent = "parent"
    """The first depends on the second"""

    child = "child"
    """The first is depended on by the second"""

    cyclic = "cyclic"
    """The first depends on the second and vice versa"""

    unrelated = "unrelated"
    """The two files are unrelated"""


@dataclass
class FileDependencyGraphNode:
    """A single node within the file dependency graph, with a reference to its
    parents and children.
    """

    path: str
    """The path to the file from the root of the project. Typically, this
    starts with src/public
    """

    filesize: int
    """The size of the file in bytes"""

    mtime: float
    """The last content modified time for the file"""

    inode: int
    """The inode of the file"""

    parents: List["FileDependencyGraphNode"]
    """The files which depend on this file."""

    children: List["FileDependencyGraphNode"]
    """The files which this file depends on."""

    def __eq__(self, other: "FileDependencyGraphNode") -> bool:
        """Determines if this graph node is logically identical to the
        given graph node. This will recursively expand the parents and
        children; this can handle cyclic graphs.

        Args:
            other (FileDependencyGraphNode): The other graph node

        Returns:
            bool: True if the other node is logically identical, false
                otherwise.
        """
        if not isinstance(other, FileDependencyGraphNode):
            return False

        if self.path != other.path:
            return False
        if self.filesize != other.filesize:
            return False
        if self.mtime != other.mtime:
            return False
        if self.inode != other.inode:
            return False

        my_seen_nodes: Dict[
            str,
            List[
                Tuple[
                    "FileDependencyGraphNode",
                    List[Tuple["FileDependencyGraphNode", Optional[bool]]],
                ]
            ],
        ] = {}
        other_seen_nodes: Dict[
            str,
            List[
                Tuple[
                    "FileDependencyGraphNode",
                    List[Tuple["FileDependencyGraphNode", Optional[bool]]],
                ]
            ],
        ] = {}

        def cmp(
            mine: "FileDependencyGraphNode", others: "FileDependencyGraphNode"
        ) -> Optional[bool]:
            if mine.path != others.path:
                return False
            if mine.filesize != others.filesize:
                return False
            if mine.mtime != others.mtime:
                return False
            if mine.inode != others.inode:
                return False
            if len(mine.parents) != len(others.parents):
                return False
            if len(mine.children) != len(others.children):
                return False

            mine_list = None
            if mine.path in my_seen_nodes:
                mine_with_same_path = my_seen_nodes[mine.path]
                for mine_with_same_path_entry in mine_with_same_path:
                    if mine_with_same_path_entry[0] is mine:
                        mine_list = mine_with_same_path_entry[1]
                        break
                else:
                    mine_list = []
                    my_seen_nodes[mine.path].append((mine, mine_list))
            else:
                mine_list = []
                my_seen_nodes[mine.path] = [(mine, mine_list)]

            for (node, are_the_same) in mine_list:
                if node is others:
                    return are_the_same

            others_list = None
            if others.path in other_seen_nodes:
                others_with_same_path = other_seen_nodes[others.path]
                for others_with_same_path_entry in others_with_same_path:
                    if others_with_same_path_entry[0] is others:
                        others_list = others_with_same_path_entry[1]
                        break
                else:
                    others_list = []
                    other_seen_nodes[others.path].append((others, others_list))
            else:
                others_list = []
                other_seen_nodes[others.path] = [(others, others_list)]

            for (node, are_the_same) in others_list:
                if node is mine:
                    return are_the_same

            mine_list.append((others, None))
            mine_list_idx = len(mine_list) - 1
            others_list.append((mine, None))
            others_list_idx = len(others_list) - 1

            parents_mismatch = any(
                cmp(a, b) is False for a, b in zip(mine.parents, others.parents)
            )
            if parents_mismatch:
                mine_list[mine_list_idx] = (others, False)
                others_list[others_list_idx] = (mine, False)
                return False

            children_mismatch = any(
                cmp(a, b) is False for a, b in zip(mine.children, others.children)
            )
            if children_mismatch:
                mine_list[mine_list_idx] = (others, False)
                others_list[others_list_idx] = (mine, False)
                return False

            mine_list[mine_list_idx] = (others, True)
            others_list[others_list_idx] = (mine, True)

            return True

        return cmp(self, other) is True


class FileDependencyGraph:
    """Describes which files depend on which other files. This distinguishes A depending on B
    from B depending on A.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, FileDependencyGraphNode] = {}
        """The nodes in the adjacency list, keyed by their path"""

    def __eq__(self, other: "FileDependencyGraph") -> bool:
        """Determines if this graph is identical to the other graph. This can
        handle cyclic graphs.

        Args:
            other (FileDependencyGraph): The graph to compare to

        Returns:
            bool: True if the two graphs are logically equivalent, false if they
                are not.
        """
        if not isinstance(other, FileDependencyGraph):
            return False

        if len(self.nodes) != len(other.nodes):
            return False
        for path, node in self.nodes.items():
            if path not in other.nodes:
                return False
            if node != other.nodes[path]:
                return False
        return True

    def store(self, fp: io.FileIO, format: Literal["json"] = "json") -> None:
        """Stores this graph in the given file, so that it can be loaded
        with load

        Args:
            fp (io.FileIO): The object to write the graph to
            format (str): The format to write the file in. Currently only
                json is supported

        Raises:
            ValueError: if the format is not supported
        """
        if format == "json":
            print("{", file=fp, end="")
            for idx, (path, node) in enumerate(self.nodes.items()):
                if idx > 0:
                    print(",", file=fp, end="")
                json.dump(path, fp)
                print(':{"parents":', file=fp, end="")
                json.dump([parent.path for parent in node.parents], fp)
                print(',"children":', file=fp, end="")
                json.dump([child.path for child in node.children], fp),
                print(',"metadata":', file=fp, end="")
                json.dump(
                    {
                        "filesize": node.filesize,
                        "mtime": node.mtime,
                        "inode": node.inode,
                    },
                    fp,
                )
                print("}", file=fp, end="")
            print("}", file=fp)
        else:
            raise ValueError(f"Unknown format: {format}")

    @classmethod
    def load(
        kls, fp: io.FileIO, format: Literal["json"] = "json"
    ) -> "FileDependencyGraph":
        """Loads the graph from the given file.

        Args:
            fp (io.FileIO): The object to read the graph from
            format (str): The format to read the file in. Currently only
                json is supported

        Raises:
            ValueError: if the format is not supported
        """
        if format == "json":
            nodes: Dict[str, FileDependencyGraphNode] = {}
            for path, item in json.load(fp).items():
                node: FileDependencyGraphNode = nodes.get(path)
                if node is None:
                    node = FileDependencyGraphNode(path, 0, 0, 0, [], [])
                    nodes[path] = node

                node.mtime = item["metadata"]["mtime"]
                node.filesize = item["metadata"]["filesize"]
                node.inode = item["metadata"]["inode"]

                for parent in item["parents"]:
                    parent_node = nodes.get(parent)
                    if parent_node is None:
                        parent_node = FileDependencyGraphNode(parent, 0, 0, 0, [], [])
                        nodes[parent] = parent_node
                    node.parents.append(parent_node)

                for child in item["children"]:
                    child_node = nodes.get(child)
                    if child_node is None:
                        child_node = FileDependencyGraphNode(child, 0, 0, 0, [], [])
                        nodes[child] = child_node
                    node.children.append(child_node)
            res = kls()
            res.nodes = nodes
            return res
        else:
            raise ValueError(f"Unknown format: {format}")

    def __contains__(self, a: str) -> bool:
        """Determines if the given file is in the graph

        Args:
            a (str): The file to check

        Returns:
            True if the file is in the graph, False otherwise
        """
        return a in self.nodes

    def check_file(self, a: str, filesize: int, mtime: float, inode: int) -> bool:
        """Checks if we have an exact match for the file with the given name

        Args:
            a (str): The path to check
            filesize (int): The filesize to check
            mtime (int): The mtime to check
            inode (int): The inode to check

        Returns:
            True if the file is in the graph and has the given metadata,
            False otherwise
        """
        a_node = self.nodes.get(a)
        if a_node is None:
            return False
        return (
            a_node.filesize == filesize
            and a_node.mtime == mtime
            and a_node.inode == inode
        )

    def check_direct_relationship(self, a: str, b: str) -> FileRelationship:
        """Compares the relationship between a and b. This is analagous
        to the standard adjacency test, except distinguishing which one
        is a parent.

        Args:
            a (str): The first path
            b (str): The second path

        Raises:
            ValueError: if a is not a file in the graph
            ValueError: if b is not a file in the graph
            ValueError: if a == b

        Returns:
            The immediate relationship between a and b. This can be cyclic
            if a is a parent of b and b is a parent of a, but this will not
            return cyclic if cycle is longer.
        """
        if a == b:
            raise ValueError(f"{a=} is equal to {b=}")
        a_node = self.nodes.get(a)
        if a_node is None:
            raise ValueError(f"{a=} is not a file in the graph")
        b_is_parent_of_a = any(node.path == b for node in a_node.parents)
        b_is_child_of_a = any(node.path == b for node in a_node.children)
        if b_is_parent_of_a and b_is_child_of_a:
            return FileRelationship.cyclic
        if b_is_parent_of_a:
            return FileRelationship.child
        if b_is_child_of_a:
            return FileRelationship.parent
        if b not in self.nodes:
            raise ValueError(f"{b=} is not a file in the graph")
        return FileRelationship.unrelated

    def check_nested_relationship(self, a: str, b: str) -> FileRelationship:
        """Checks how a and b are related in general. This will recursively
        check the graph, handling cycles appropriately.

        Args:
            a (str): The first path
            b (str): The second path

        Raises:
            ValueError: if a is not a file in the graph
            ValueError: if b is not a file in the graph
            ValueError: if a == b
        """
        if a == b:
            raise ValueError(f"{a=} is equal to {b=}")

        a_node = self.nodes.get(a)
        if a_node is None:
            raise ValueError(f"{a=} is not a file in the graph")

        if b not in self.nodes:
            raise ValueError(f"{b=} is not a file in the graph")

        def check_tree(
            node: FileDependencyGraphNode, dir: Literal["child", "parent"]
        ) -> bool:
            seen_paths: Set[str] = set()
            queue: List[FileDependencyGraphNode] = []

            if dir == "child":
                for child in node.children:
                    queue.append(child)
                    seen_paths.add(child.path)
            else:
                for parent in node.parents:
                    queue.append(parent)
                    seen_paths.add(parent.path)

            while queue:
                item = queue.pop(0)

                if item.path == b:
                    return True

                if dir == "child":
                    for child in item.children:
                        if child.path not in seen_paths:
                            queue.append(child)
                            seen_paths.add(child.path)
                else:
                    for parent in item.parents:
                        if parent.path not in seen_paths:
                            queue.append(parent)
                            seen_paths.add(parent.path)

            return False

        b_is_parent_of_a = check_tree(a_node, "parent")
        b_is_child_of_a = check_tree(a_node, "child")

        if b_is_parent_of_a and b_is_child_of_a:
            return FileRelationship.cyclic
        if b_is_parent_of_a:
            return FileRelationship.child
        if b_is_child_of_a:
            return FileRelationship.parent
        return FileRelationship.unrelated

    def get_parents(self, a: str) -> List[str]:
        """Gets the parents of the given file. This is analagous to the
        standard neighbors test, except only for parents.

        Args:
            a (str): The path to get the parents of

        Raises:
            ValueError: if a is not a file in the graph

        Returns:
            A list of the parents of the given file
        """
        a_node = self.nodes.get(a)
        if a_node is None:
            raise ValueError(f"{a=} is not a file in the graph")
        return [parent.path for parent in a_node.parents]

    def get_children(self, a: str) -> List[str]:
        """Gets the children of the given file. This is analagous to the
        standard neighbors test, except only for children.

        Args:
            a (str): The path to get the children of

        Raises:
            ValueError: if a is not a file in the graph

        Returns:
            A list of the children of the given file
        """
        a_node = self.nodes.get(a)
        if a_node is None:
            raise ValueError(f"{a=} is not a file in the graph")
        return [child.path for child in a_node.children]

    def add_file(
        self,
        a: str,
        filesize: int,
        mtime: float,
        inode: int,
        children: Optional[List[str]] = None,
    ) -> None:
        """Adds the given file to the graph. May optionally specify the children
        of the file; if unspecified, no children is assumed.

        This operation cannot produce cycles in the graph.

        Args:
            a (str): The file to add to the graph
            children (list[str], None): The children of the file, or none for
                no children

        Raises:
            ValueError: if a is already a file in the graph
            ValueError: if any of the children are not in the graph
        """
        if a in self.nodes:
            raise ValueError(f"{a=} is already a file in the graph")

        if children and any(c not in self.nodes for c in children):
            bad_children = [c for c in children if c not in self.nodes]
            raise ValueError(f"{bad_children=} are not files in the graph")

        node = FileDependencyGraphNode(a, filesize, mtime, inode, [], [])
        if children:
            for child in children:
                child_node = self.nodes[child]
                child_node.parents.append(node)
                node.children.append(child_node)

        self.nodes[a] = node

    def remove_file(
        self, a: str, clear_parents: bool = False, clear_children: bool = False
    ) -> None:
        """Removes the given file from the graph.

        Args:
            a (str): The file to remove
            clear_parents (bool): If False and the file has parents, then an error
                is raised. If True and the file has parents, the edges are removed
                before the file is removed
            clear_children (bool): If False and the file has children, then an error
                is raised. If True and the file has children, the edges are removed
                before the file is removed

        Raises:
            ValueError: if a is not a file in the graph
            ValueError: if a has any parents in the graph and clear_parents is False
            ValueError: if a has any children in the graph and clear_children is False
        """
        node = self.nodes.get(a)
        if node is None:
            raise ValueError(f"{a=} is not a file in the graph")

        if node.parents and not clear_parents:
            raise ValueError(
                f"{a=} has parents in the graph and clear_parents is False"
            )

        if node.children and not clear_children:
            raise ValueError(
                f"{a=} has children in the graph and clear_children is False"
            )

        if node.parents:
            for parent in node.parents:
                parent.children.remove(node)
            node.parents.clear()

        if node.children:
            for child in node.children:
                child.parents.remove(node)
            node.children.clear()

        del self.nodes[a]

    def set_children(
        self, a: str, children: List[str], prevent_cycles: bool = True
    ) -> None:
        """Updates the children for the given file.

        Args:
            a (str): The path of the node to update
            children (list[str]): The new children for the node
            prevent_cycles (bool): If True, we will raise an error if a would have
                a cyclic relationship with another file after this operation. Note
                that this will cause an error even if the cycle is not new.

        Raises:
            ValueError: if a is not a file in the graph
            ValueError: if any of the children of a are not files in the graph
            ValueError: if a would have a cyclic relationship with another file
              and prevent_cycles is True
        """
        node = self.nodes.get(a)
        if node is None:
            raise ValueError(f"{a=} is not a file in the graph")
        if any(c not in self.nodes for c in children):
            bad_children = [c for c in children if c not in self.nodes]
            raise ValueError(f"{bad_children=} are not files in the graph")
        if prevent_cycles and any(
            self.check_nested_relationship(a, c)
            in (FileRelationship.cyclic, FileRelationship.child)
            for c in children
        ):
            bad_children = [
                c
                for c in children
                if self.check_nested_relationship(a, c)
                in (FileRelationship.cyclic, FileRelationship.child)
            ]
            raise ValueError(
                f"{bad_children=} would have a cyclic relationship with the file {a=}"
            )

        for child in node.children:
            child.parents.remove(node)
        node.children.clear()
        for child in children:
            child_node = self.nodes[child]
            child_node.parents.append(node)
            node.children.append(child_node)

    def __repr__(self) -> str:
        return f"FileDependencyGraph({self.nodes=})"
