import networkx as nx


class ModuleGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(
        self,
        parsed_files: list[dict],
        dependencies: list[dict],
    ) -> dict:

        self.graph.clear()

        self._add_modules(parsed_files)
        self._add_dependencies(dependencies)

        return self.to_dict()

    def _add_modules(self, parsed_files: list[dict]):
        for parsed_file in parsed_files:
            file_path = parsed_file.get("file")

            if not file_path:
                continue

            self.graph.add_node(
                file_path,
                language=parsed_file.get("language"),
                has_errors=parsed_file.get("has_errors", False),
            )

    def _add_dependencies(self, dependencies: list[dict]):
        for dependency_data in dependencies:
            source_file = dependency_data.get("file")

            if not source_file:
                continue

            for target_file in dependency_data.get(
                "internal_dependencies",
                [],
            ):
                self.graph.add_edge(
                    source_file,
                    target_file,
                    relationship="imports",
                )

    def to_dict(self) -> dict:
        nodes = []

        for node, attributes in self.graph.nodes(data=True):
            nodes.append(
                {
                    "id": node,
                    **attributes,
                }
            )

        edges = []

        for source, target, attributes in self.graph.edges(data=True):
            edges.append(
                {
                    "source": source,
                    "target": target,
                    **attributes,
                }
            )

        return {
            "statistics": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
            },
            "nodes": nodes,
            "edges": edges,
        }