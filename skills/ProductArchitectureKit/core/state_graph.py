from collections import defaultdict
from typing import Callable, Any

try:
    import networkx as nx
except ImportError:

    class _FallbackDiGraph:
        def __init__(self):
            self._succ: dict[str, dict[str, dict]] = {}
            self._pred: dict[str, set[str]] = defaultdict(set)

        def add_node(self, node_id: str):
            self._succ.setdefault(node_id, {})

        def add_edge(self, u: str, v: str, **attrs):
            self._succ.setdefault(u, {})[v] = attrs
            self._succ.setdefault(v, {})
            self._pred[v].add(u)

        def successors(self, node_id: str):
            return list(self._succ.get(node_id, {}).keys())

        def predecessors(self, node_id: str):
            return list(self._pred.get(node_id, set()))

        def remove_node(self, node_id: str):
            self._succ.pop(node_id, None)
            self._pred.pop(node_id, None)
            for nbrs in self._succ.values():
                nbrs.pop(node_id, None)
            for preds in self._pred.values():
                preds.discard(node_id)

        def clear(self):
            self._succ.clear()
            self._pred.clear()

    class _NXShim:
        DiGraph = _FallbackDiGraph

    nx = _NXShim()  # type: ignore


class StateGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: dict[str, dict] = {}
        self.edges: list[tuple] = []

    def add_node(self, node_id: str, state: dict):
        self.graph.add_node(node_id)
        self.nodes[node_id] = state

    def add_edge(
        self, from_node: str, to_node: str, condition: Callable[..., Any] | None = None
    ):
        self.graph.add_edge(from_node, to_node, condition=condition)
        self.edges.append((from_node, to_node))

    def get_next_states(self, node_id: str) -> list[str]:
        return list(self.graph.successors(node_id))

    def get_previous_states(self, node_id: str) -> list[str]:
        return list(self.graph.predecessors(node_id))

    def traverse(
        self, start_node: str, condition: Callable[..., Any] | None = None
    ) -> list[str]:
        visited = set()
        queue = [start_node]
        path = []
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                path.append(node)
                for neighbor in self.get_next_states(node):
                    if neighbor not in visited:
                        if condition is None or condition(
                            self.nodes[node], self.nodes[neighbor]
                        ):
                            queue.append(neighbor)
        return path

    def get_state(self, node_id: str) -> dict:
        return self.nodes.get(node_id, {})

    def update_state(self, node_id: str, state: dict):
        if node_id in self.nodes:
            self.nodes[node_id].update(state)
        else:
            self.add_node(node_id, state)

    def remove_node(self, node_id: str):
        self.graph.remove_node(node_id)
        self.nodes.pop(node_id, None)
        self.edges = [(f, t) for f, t in self.edges if f != node_id and t != node_id]

    def clear(self):
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
