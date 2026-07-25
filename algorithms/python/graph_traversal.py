#!/usr/bin/env python3
"""
Graph traversal utilities.

Implements breadth-first search (BFS) and depth-first search (DFS)
over a graph represented as an adjacency list (dict[node] -> list[neighbors]).
Both traversals return the list of nodes in the order they were visited.
"""

from collections import deque
from typing import Any, Dict, Hashable, Iterable, List


Graph = Dict[Hashable, Iterable[Hashable]]


def bfs(graph: Graph, start: Hashable) -> List[Hashable]:
    """Breadth-first traversal starting from `start`."""
    if start not in graph:
        raise ValueError(f"Start node {start!r} not in graph")

    visited = {start}
    order = []
    queue = deque([start])

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, ()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def dfs(graph: Graph, start: Hashable) -> List[Hashable]:
    """Depth-first traversal starting from `start` (iterative, preserves neighbor order)."""
    if start not in graph:
        raise ValueError(f"Start node {start!r} not in graph")

    visited = set()
    order = []
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        # Push in reverse so the first neighbor is processed first (matches recursive DFS order).
        for neighbor in reversed(list(graph.get(node, ()))):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


def main() -> None:
    graph: Graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "F"],
        "F": ["C", "E"],
    }

    print("BFS from A:", bfs(graph, "A"))
    print("DFS from A:", dfs(graph, "A"))


if __name__ == "__main__":
    main()
