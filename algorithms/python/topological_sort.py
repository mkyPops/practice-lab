"""
Topological sort using Kahn's algorithm.

Given a directed graph represented as an adjacency list (dict mapping each
node to an iterable of nodes it points to), compute a topological ordering
of the nodes. If the graph contains a cycle, no valid ordering exists and a
ValueError is raised instead.
"""

from collections import deque
from typing import Dict, Hashable, Iterable, List


def topological_sort(graph: Dict[Hashable, Iterable[Hashable]]) -> List[Hashable]:
    """Return a topologically sorted list of nodes from `graph`.

    Raises:
        ValueError: if the graph contains a cycle.
    """
    # Ensure every referenced node has an entry, and compute in-degrees.
    in_degree = {node: 0 for node in graph}
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            in_degree.setdefault(neighbor, 0)
            in_degree[neighbor] += 1
            graph.setdefault(neighbor, [])

    # Start with all nodes that have no incoming edges.
    queue = deque(node for node, deg in in_degree.items() if deg == 0)
    order: List[Hashable] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(in_degree):
        raise ValueError("Graph contains at least one cycle; "
                          "topological sort is not possible.")

    return order


def main() -> None:
    # Example graph: classic "getting dressed" dependency chain.
    graph = {
        "shirt": ["jacket"],
        "tie": ["jacket"],
        "jacket": [],
        "pants": ["shoes", "jacket"],
        "underwear": ["pants"],
        "socks": ["shoes"],
        "shoes": [],
    }

    try:
        order = topological_sort(graph)
        print("Topological order:", order)
    except ValueError as exc:
        print("Error:", exc)

    # Example graph with a cycle to demonstrate error handling.
    cyclic_graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    try:
        topological_sort(cyclic_graph)
    except ValueError as exc:
        print("Error:", exc)


if __name__ == "__main__":
    main()
