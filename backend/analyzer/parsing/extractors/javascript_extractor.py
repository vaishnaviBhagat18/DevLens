from backend.analyzer.parsing.extractors.base_extractor import BaseExtractor


class JavaScriptExtractor(BaseExtractor):

    EXPRESS_METHODS = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "use",
    }

    def extract(self, root_node) -> dict:
        result = {
            "imports": [],
            "functions": [],
            "classes": [],
            "exports": [],
            "routes": [],
        }

        self._walk(root_node, result)

        return result

    def _walk(self, node, result: dict):
        if node.type == "import_statement":
            self._extract_import(node, result)

        elif node.type == "function_declaration":
            self._extract_function(node, result)

        elif node.type == "class_declaration":
            self._extract_class(node, result)

        elif node.type == "export_statement":
            self._extract_export(node, result)

        elif node.type == "assignment_expression":
            self._extract_commonjs_export(node, result)

        elif node.type == "call_expression":
            self._extract_require(node, result)
            self._extract_express_route(node, result)

        elif node.type == "variable_declarator":
            self._extract_variable_function(node, result)

        for child in node.children:
            self._walk(child, result)

    def _extract_import(self, node, result: dict):
        source_node = node.child_by_field_name("source")

        if source_node is None:
            return

        source = self._clean_string(
            self.get_node_text(source_node)
        )

        self._add_unique(
            result["imports"],
            {
                "source": source,
                "type": "import",
            },
        )

    def _extract_require(self, node, result: dict):
        function_node = node.child_by_field_name("function")
        arguments_node = node.child_by_field_name("arguments")

        if function_node is None or arguments_node is None:
            return

        function_name = self.get_node_text(function_node)

        if function_name != "require":
            return

        for child in arguments_node.named_children:
            if child.type == "string":
                source = self._clean_string(
                    self.get_node_text(child)
                )

                self._add_unique(
                    result["imports"],
                    {
                        "source": source,
                        "type": "require",
                    },
                )
                break

    def _extract_function(self, node, result: dict):
        name_node = node.child_by_field_name("name")

        if name_node is None:
            return

        self._add_unique(
            result["functions"],
            {
                "name": self.get_node_text(name_node),
                "type": "function",
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )

    def _extract_class(self, node, result: dict):
        name_node = node.child_by_field_name("name")

        if name_node is None:
            return

        self._add_unique(
            result["classes"],
            {
                "name": self.get_node_text(name_node),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )

    def _extract_export(self, node, result: dict):
        self._add_unique(
            result["exports"],
            {
                "type": "es_module",
                "text": self.get_node_text(node),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )

    def _extract_commonjs_export(self, node, result: dict):
        left_node = node.child_by_field_name("left")
        right_node = node.child_by_field_name("right")

        if left_node is None or right_node is None:
            return

        left_text = self.get_node_text(left_node)

        if not (
            left_text == "module.exports"
            or left_text.startswith("exports.")
            or left_text.startswith("module.exports.")
        ):
            return

        self._add_unique(
            result["exports"],
            {
                "type": "commonjs",
                "target": left_text,
                "value": self.get_node_text(right_node),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )

    def _extract_express_route(self, node, result: dict):
        function_node = node.child_by_field_name("function")
        arguments_node = node.child_by_field_name("arguments")

        if function_node is None or arguments_node is None:
            return

        if function_node.type != "member_expression":
            return

        object_node = function_node.child_by_field_name("object")
        property_node = function_node.child_by_field_name("property")

        if object_node is None or property_node is None:
            return

        method = self.get_node_text(property_node)

        if method not in self.EXPRESS_METHODS:
            return

        route_path = None

        for child in arguments_node.named_children:
            if child.type in {"string", "template_string"}:
                route_path = self._clean_string(
                    self.get_node_text(child)
                )
                break

        # Calls such as app.use(cors()) have no route path.
        # We don't treat those as API routes.
        if route_path is None:
            return

        self._add_unique(
            result["routes"],
            {
                "object": self.get_node_text(object_node),
                "method": method.upper(),
                "path": route_path,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )

    def _clean_string(self, value: str) -> str:
        value = value.strip()

        if (
            len(value) >= 2
            and value[0] in {"'", '"', "`"}
            and value[-1] == value[0]
        ):
            return value[1:-1]

        return value

    def _add_unique(self, collection: list, item: dict):
        if item not in collection:
            collection.append(item)

    def _extract_variable_function(self, node, result: dict):
        name_node = node.child_by_field_name("name")
        value_node = node.child_by_field_name("value")

        if name_node is None or value_node is None:
            return

        if value_node.type not in {
            "arrow_function",
            "function_expression",
        }:
            return

        self._add_unique(
            result["functions"],
            {
                "name": self.get_node_text(name_node),
                "type": (
                    "arrow_function"
                    if value_node.type == "arrow_function"
                    else "function_expression"
                ),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            },
        )