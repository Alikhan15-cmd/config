"""Recursive DFS dependency graph builder with cycle and depth control."""

from src.collector import get_direct_dependencies
from src.constants import ZERO


class DependencyGraph:
    """Represents a directed dependency graph."""

    def __init__(self):
        """Initialize empty graph structures."""
        self.nodes = set()
        self.edges = []
        self.adjacency = {}
        self.cycles = []

    def add_node(self, node: str) -> None:
        """Add node to graph if not present."""
        self.nodes.add(node)
        if node not in self.adjacency:
            self.adjacency[node] = []

    def add_edge(self, source: str, target: str) -> None:
        """Add directed edge from source to target."""
        self.add_node(source)
        self.add_node(target)
        edge = (source, target)
        if edge not in self.edges:
            self.edges.append(edge)
            self.adjacency[source].append(target)

    def add_cycle(self, cycle_path: list[str]) -> None:
        """Record detected cycle path."""
        if cycle_path not in self.cycles:
            self.cycles.append(cycle_path)


def _should_filter(node_name: str, filter_substring: str) -> bool:
    """Check if node should be filtered out by substring."""
    clean_sub = filter_substring.strip()
    if len(clean_sub) == ZERO:
        return False
    return clean_sub.lower() in node_name.lower()


def _handle_cycle_detection(
    source: str,
    target: str,
    recursion_stack: list[str],
    graph: DependencyGraph,
) -> None:
    """Process and record cycle when target is in recursion stack."""
    graph.add_edge(source, target)
    target_idx = recursion_stack.index(target)
    cycle = recursion_stack[target_idx:] + [target]
    graph.add_cycle(cycle)


def _dfs_visit(
    node: str,
    depth: int,
    max_depth: int,
    filter_sub: str,
    context: tuple,
    state: tuple,
) -> None:
    """Recursively traverse dependencies using DFS."""
    version, repo_url, test_mode = context
    visited, rec_stack, graph = state

    graph.add_node(node)
    visited.add(node)
    rec_stack.append(node)

    if depth < max_depth:
        cur_ver = version if depth == ZERO else ""
        raw_deps = get_direct_dependencies(node, cur_ver, repo_url, test_mode)

        for dep in raw_deps:
            if _should_filter(dep, filter_sub):
                continue
            if dep in rec_stack:
                _handle_cycle_detection(node, dep, rec_stack, graph)
            else:
                graph.add_edge(node, dep)
                if dep not in visited:
                    _dfs_visit(
                        dep,
                        depth + 1,
                        max_depth,
                        filter_sub,
                        context,
                        state,
                    )

    rec_stack.pop()


def build_dependency_graph(
    root_package: str,
    version: str,
    repo_url: str,
    test_mode: bool,
    max_depth: int,
    filter_substring: str,
) -> DependencyGraph:
    """Build dependency graph starting from root package via recursive DFS."""
    graph = DependencyGraph()
    if _should_filter(root_package, filter_substring):
        return graph

    visited = set()
    rec_stack = []

    context = (version, repo_url, test_mode)
    state = (visited, rec_stack, graph)

    _dfs_visit(
        node=root_package,
        depth=ZERO,
        max_depth=max_depth,
        filter_sub=filter_substring,
        context=context,
        state=state,
    )
    return graph
