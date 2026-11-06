// dijkstra.cpp
// Computes single-source shortest paths on a weighted, directed graph
// using Dijkstra's algorithm with an adjacency list and a min-priority queue.

#include <iostream>
#include <vector>
#include <queue>
#include <limits>

using Edge = std::pair<int, long long>; // (destination, weight)

// Returns shortest distances from `src` to every vertex in a graph with
// `numVertices` nodes, given as an adjacency list. Unreachable vertices
// retain distance = infinity.
std::vector<long long> dijkstra(const std::vector<std::vector<Edge>>& graph,
                                 int src) {
    const long long INF = std::numeric_limits<long long>::max();
    std::vector<long long> dist(graph.size(), INF);
    dist[src] = 0;

    // Min-heap of (distance, vertex), ordered by smallest distance first.
    using State = std::pair<long long, int>;
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;
    pq.emplace(0, src);

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue; // stale entry, skip

        for (const auto& [v, w] : graph[u]) {
            long long nd = d + w;
            if (nd < dist[v]) {
                dist[v] = nd;
                pq.emplace(nd, v);
            }
        }
    }
    return dist;
}

int main() {
    const int numVertices = 6;
    std::vector<std::vector<Edge>> graph(numVertices);

    auto addEdge = [&](int u, int v, long long w) {
        graph[u].emplace_back(v, w);
        graph[v].emplace_back(u, w); // undirected for this example
    };

    addEdge(0, 1, 7);
    addEdge(0, 2, 9);
    addEdge(0, 5, 14);
    addEdge(1, 2, 10);
    addEdge(1, 3, 15);
    addEdge(2, 3, 11);
    addEdge(2, 5, 2);
    addEdge(3, 4, 6);
    addEdge(4, 5, 9);

    int source = 0;
    std::vector<long long> distances = dijkstra(graph, source);

    std::cout << "Shortest distances from vertex " << source << ":\n";
    for (int i = 0; i < numVertices; ++i) {
        std::cout << "  to " << i << ": " << distances[i] << '\n';
    }
    return 0;
}
