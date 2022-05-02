import helper  # noqa
import unittest
import os
from vanillaplusjs.build.graph import FileDependencyGraph, FileRelationship


class Test(unittest.TestCase):
    def test_two_empty_are_equal(self):
        a = FileDependencyGraph()
        b = FileDependencyGraph()
        self.assertEqual(a, b)

    def test_single_same_are_same(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        b = FileDependencyGraph()
        b.add_file("a.js", 0, 0, 0)
        self.assertEqual(a, b)

    def test_differ_on_filename(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        b = FileDependencyGraph()
        b.add_file("b.js", 0, 0, 0)
        self.assertNotEqual(a, b)

    def test_differ_on_filesize(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        b = FileDependencyGraph()
        b.add_file("a.js", 1, 0, 0)
        self.assertNotEqual(a, b)

    def test_differ_on_mtime(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        b = FileDependencyGraph()
        b.add_file("a.js", 0, 1, 0)
        self.assertNotEqual(a, b)

    def test_differ_on_inode(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        b = FileDependencyGraph()
        b.add_file("a.js", 0, 0, 1)
        self.assertNotEqual(a, b)

    def test_differ_on_relationship(self):
        a = FileDependencyGraph()
        a.add_file("child.js", 0, 0, 0)
        a.add_file("parent.js", 0, 0, 0, ["child.js"])
        b = FileDependencyGraph()
        b.add_file("parent.js", 0, 0, 0)
        b.add_file("child.js", 0, 0, 0, ["parent.js"])
        self.assertNotEqual(a, b)

    def test_equal_cyclic(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        a.add_file("b.js", 0, 0, 0, ["a.js"])
        a.set_children("a.js", ["b.js"])

        b = FileDependencyGraph()
        b.add_file("a.js", 0, 0, 0)
        b.add_file("b.js", 0, 0, 0, ["a.js"])
        b.set_children("a.js", ["b.js"])

        self.assertEqual(a, b)

    def test_repr_cyclic(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        a.add_file("b.js", 0, 0, 0, ["a.js"])
        a.set_children("a.js", ["b.js"])
        repr(a)
        self.assertTrue(True)

    def test_differ_on_cyclic(self):
        a = FileDependencyGraph()
        a.add_file("a.js", 0, 0, 0)
        a.add_file("b.js", 0, 0, 0, ["a.js"])
        a.set_children("a.js", ["b.js"])
        b = FileDependencyGraph()
        b.add_file("a.js", 0, 0, 0)
        b.add_file("b.js", 1, 0, 0, ["a.js"])
        b.set_children("a.js", ["b.js"])
        self.assertNotEqual(a, b)

    def test_save_empty(self):
        graph = FileDependencyGraph()
        try:
            with open("test.json", "w") as f:
                graph.store(f)

            with open("test.json", "r") as f:
                new_graph = FileDependencyGraph.load(f)

            self.assertEqual(new_graph, graph)
        finally:
            if os.path.exists("test.json"):
                os.unlink("test.json")

    def test_save_single(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        try:
            with open("test.json", "w") as f:
                graph.store(f)
            with open("test.json", "r") as f:
                new_graph = FileDependencyGraph.load(f)
            self.assertEqual(new_graph, graph)
        finally:
            if os.path.exists("test.json"):
                os.unlink("test.json")

    def test_save_cyclic(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        graph.set_children("a.js", ["b.js"])
        try:
            with open("test.json", "w") as f:
                graph.store(f)
            with open("test.json", "r") as f:
                new_graph = FileDependencyGraph.load(f)
            self.assertEqual(new_graph, graph)
        finally:
            if os.path.exists("test.json"):
                os.unlink("test.json")

    def test_check_relationship_dne(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0)
        self.assertEqual(
            graph.check_direct_relationship("a.js", "b.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "b.js"), FileRelationship.unrelated
        )

    def test_check_relationship_parent(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        self.assertEqual(
            graph.check_direct_relationship("a.js", "b.js"), FileRelationship.child
        )
        self.assertEqual(
            graph.check_direct_relationship("b.js", "a.js"), FileRelationship.parent
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "b.js"), FileRelationship.child
        )
        self.assertEqual(
            graph.check_nested_relationship("b.js", "a.js"), FileRelationship.parent
        )

    def test_check_relationship_distant_parent(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        graph.add_file("c.js", 0, 0, 0, ["b.js"])
        self.assertEqual(
            graph.check_direct_relationship("a.js", "c.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_direct_relationship("c.js", "a.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "c.js"), FileRelationship.child
        )
        self.assertEqual(
            graph.check_nested_relationship("c.js", "a.js"), FileRelationship.parent
        )

    def test_check_relationship_cyclic(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        graph.set_children("a.js", ["b.js"])
        self.assertEqual(
            graph.check_direct_relationship("a.js", "b.js"), FileRelationship.cyclic
        )
        self.assertEqual(
            graph.check_direct_relationship("b.js", "a.js"), FileRelationship.cyclic
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "b.js"), FileRelationship.cyclic
        )
        self.assertEqual(
            graph.check_nested_relationship("b.js", "a.js"), FileRelationship.cyclic
        )

    def test_check_relationship_distant_cyclic_1(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        graph.add_file("c.js", 0, 0, 0, ["b.js"])
        graph.add_file("d.js", 0, 0, 0, ["c.js"])
        graph.set_children("a.js", ["d.js"])
        self.assertEqual(
            graph.check_direct_relationship("a.js", "c.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_direct_relationship("c.js", "a.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "c.js"), FileRelationship.cyclic
        )
        self.assertEqual(
            graph.check_nested_relationship("c.js", "a.js"), FileRelationship.cyclic
        )

    def test_check_relationship_distant_cyclic_2(self):
        graph = FileDependencyGraph()
        graph.add_file("a.js", 0, 0, 0)
        graph.add_file("b.js", 0, 0, 0, ["a.js"])
        graph.add_file("c.js", 0, 0, 0, ["b.js"])
        graph.set_children("b.js", ["c.js"])
        self.assertEqual(
            graph.check_direct_relationship("a.js", "c.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_direct_relationship("c.js", "a.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_nested_relationship("a.js", "c.js"), FileRelationship.unrelated
        )
        self.assertEqual(
            graph.check_nested_relationship("c.js", "a.js"), FileRelationship.unrelated
        )


if __name__ == "__main__":
    unittest.main()
