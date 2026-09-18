// dijkstra.cpp
// Implements Dijkstra's shortest path algorithm on a weighted directed graph
// represented as an adjacency list, using a min-priority queue for efficiency.

#include <iostream>
#include <vector>
#include <queue>
#include <limits>

using Edge = std::pair<int, int>; // {destination, weight}
using Graph = std::vector<std::vector<Edge>>;

constexpr long long INF = std::numeric_limits<long long>::max();

// Computes shortest distances from `source` to all nodes in `graph`.
std::vector<long long> dijkstra(const Graph& graph, int source) {
    int n = static_cast<int>(graph.size());
    std::vector<long long> dist(n, INF);
    dist[source] = 0;

    // Min-heap of {distance, node}, ordered by smallest distance first.
    std::priority_queue<std::pair<long long, int>,
                         std::vector<std::pair<long long, int>>,
                         std::greater<>> pq;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        // Skip stale entries left in the heap from earlier relaxations.
        if (d > dist[u]) continue;

        for (const auto& [v, weight] : graph[u]) {
            long long newDist = d + weight;
            if (newDist < dist[v]) {
                dist[v] = newDist;
                pq.push({newDist, v});
            }
        }
    }
    return dist;
}

int main() {
    int n = 6; // number of nodes, labeled 0..5
    Graph graph(n);

    // Add directed edges: graph[u].push_back({v, weight})
    graph[0].push_back({1, 7});
    graph[0].push_back({2, 9});
    graph[0].push_back({5, 14});
    graph[1].push_back({2, 10});
    graph[1].push_back({3, 15});
    graph[2].push_back({3, 11});
    graph[2].push_back({5, 2});
    graph[3].push_back({4, 6});
    graph[5].push_back({4, 9});

    int source = 0;
    std::vector<long long> distances = dijkstra(graph, source);

    std::cout << "Shortest distances from node " << source << ":\n";
    for (int i = 0; i < n; ++i) {
        std::cout << "  to " << i << ": ";
        if (distances[i] == INF) {
            std::cout << "unreachable\n";
        } else {
            std::cout << distances[i] << '\n';
        }
    }

    return 0;
}
