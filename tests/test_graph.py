"""Unit tests for recursive DFS graph building and operations."""

import os
import unittest
from src.constants import ZERO
from src.graph import DependencyGraph, build_dependency_graph


class TestGraph(unittest.TestCase):
    """Test suite for DFS dependency graph construction."""

    def test_simple_graph_traversal(self):
        """Verify full traversal on simple tree repo."""
        repo_path = os.path.join("test_repos", "simple_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=5,
            filter_substring="",
        )
        self.assertIn("A", graph.nodes)
        self.assertIn("B", graph.nodes)
        self.assertIn("C", graph.nodes)
        self.assertIn("D", graph.nodes)
        self.assertIn("E", graph.nodes)
        self.assertIn(("A", "B"), graph.edges)
        self.assertIn(("B", "D"), graph.edges)
        self.assertEqual(len(graph.cycles), ZERO)

    def test_depth_limit_zero(self):
        """Verify depth zero includes only root."""
        repo_path = os.path.join("test_repos", "simple_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=0,
            filter_substring="",
        )
        self.assertEqual(graph.nodes, {"A"})
        self.assertEqual(len(graph.edges), ZERO)

    def test_depth_limit_one(self):
        """Verify depth one includes direct dependencies only."""
        repo_path = os.path.join("test_repos", "simple_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=1,
            filter_substring="",
        )
        self.assertEqual(graph.nodes, {"A", "B", "C"})
        self.assertIn(("A", "B"), graph.edges)
        self.assertIn(("A", "C"), graph.edges)
        self.assertNotIn(("B", "D"), graph.edges)

    def test_filter_substring(self):
        """Verify packages containing substring are omitted."""
        repo_path = os.path.join("test_repos", "deep_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=5,
            filter_substring="TEST",
        )
        self.assertNotIn("TEST_HELPER", graph.nodes)

    def test_cyclic_dependencies(self):
        """Verify cycles are safely handled and detected."""
        repo_path = os.path.join("test_repos", "cyclic_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=5,
            filter_substring="",
        )
        self.assertEqual(graph.nodes, {"A", "B", "C", "D"})
        self.assertGreater(len(graph.cycles), ZERO)
        first_cycle = graph.cycles[0]
        self.assertEqual(first_cycle[0], first_cycle[-1])

    def test_diamond_dependencies(self):
        """Verify diamond dependencies keep all edges."""
        repo_path = os.path.join("test_repos", "diamond_repo.json")
        graph = build_dependency_graph(
            root_package="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
            max_depth=5,
            filter_substring="",
        )
        self.assertEqual(graph.nodes, {"A", "B", "C", "D"})
        self.assertIn(("B", "D"), graph.edges)
        self.assertIn(("C", "D"), graph.edges)


if __name__ == "__main__":
    unittest.main()
