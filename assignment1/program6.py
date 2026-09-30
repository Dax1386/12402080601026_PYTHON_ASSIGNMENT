import heapq
from collections import defaultdict, deque

def resolve_dependencies(nodes, edges):
    adj = defaultdict(set)
    in_degree = {node: 0 for node in nodes}

    for u, v in edges:
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1

    # Lexicographically smallest using Min Heap
    heap = [node for node in nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    order = []
    while heap:
        curr = heapq.heappop(heap)
        order.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(order) == len(nodes):
        print(" ".join(order))
    else:
        # Cycle detection logic using DFS
        visited = {} # 0: unvisited, 1: visiting, 2: visited
        parent = {}
        cycle = []

        def dfs(u):
            visited[u] = 1
            for v in adj[u]:
                if visited.get(v, 0) == 1:
                    # Found cycle
                    curr = u
                    cycle.append(v)
                    while curr != v:
                        cycle.append(curr)
                        curr = parent[curr]
                    cycle.append(v)
                    cycle.reverse()
                    return True
                elif visited.get(v, 0) == 0:
                    parent[v] = u
                    if dfs(v):
                        return True
            visited[u] = 2
            return False

        for node in nodes:
            if visited.get(node, 0) == 0:
                if dfs(node):
                    break
        print("CYCLE " + " ".join(cycle))

if __name__ == "__main__":
    modules = ["core", "db", "ui", "auth"]
    deps = [("ui", "auth"), ("auth", "db"), ("db", "core")]
    resolve_dependencies(modules, deps)