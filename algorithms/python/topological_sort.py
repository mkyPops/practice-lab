"""
Topological sort implementation using Kahn's algorithm.

Given a directed acyclic graph (DAG) represented as an adjacency list,
this module computes a valid topological ordering of its nodes. If the
graph contains a cycle, a ValueError is raised since no valid ordering
exists.
"""

from collections import deque
from typing import Dict, Iterable, List, TypeVar

T = TypeVar("T")


def topological_sort(graph: Dict[T, Iterable[T]]) -> List[T]:
    """
    Return a topological ordering of the nodes in `graph`.

    `graph` maps each node to an iterable of nodes it points to
    (i.e., edges go from key -> value). Nodes referenced only as
    dependencies (values) but not present as keys are treated as
    having no outgoing edges.

    Raises:
        ValueError: if the graph contains a cycle.
    """
    # Ensure every node (source or target) appears in the graph and in-degree map.
    in_degree: Dict[T, int] = {}
    for node, deps in graph.items():
        in_degree.setdefault(node, 0)
        for dep in deps:
            in_degree[dep] = in_degree.get(dep, 0) + 1

    # Normalize adjacency so lookups never fail for leaf nodes.
    adjacency: Dict[T, Iterable[T]] = {node: graph.get(node, []) for node in in_degree}

    # Start with all nodes that have no incoming edges.
    queue = deque(node for node, degree in in_degree.items() if degree == 0)
    order: List[T] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(in_degree):
        raise ValueError("Graph contains a cycle; topological sort not possible")

    return order


if __name__ == "__main__":
    # Simple demonstration.
    sample_graph = {
        "shirt": ["jacket"],
        "tie": ["jacket"],
        "jacket": [],
        "pants": ["shoes", "shirt"],
        "shoes": [],
        "socks": ["shoes"],
    }
    print(topological_sort(sample_graph))

    cyclic_graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    try:
        topological_sort(cyclic_graph)
    except ValueError as exc:
        print(f"Error: {exc}")
