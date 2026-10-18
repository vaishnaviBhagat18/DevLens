from pathlib import Path


class ContextBuilder:

    MAX_FILE_CHARS = 12000
    MAX_SOURCE_FILES = 8

    SOURCE_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".php",
        ".rb",
        ".html",
    }

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

    def build(self, analysis: dict) -> dict:
        selected_files = self._select_source_files(analysis)

        source_files = []

        for relative_path in selected_files:
            content = self._read_source_file(relative_path)

            if content is None:
                continue

            source_files.append(
                {
                    "file": relative_path,
                    "content": content,
                }
            )

        return {
            "project_name": analysis.get("project_name"),
            "technology": analysis.get("technology", {}),
            "top_level_structure": analysis.get(
                "top_level_structure",
                [],
            ),
            "important_files": analysis.get(
                "important_files",
                [],
            ),
            "dependencies": analysis.get(
                "code_analysis",
                {},
            ).get(
                "dependencies",
                [],
            ),
            "module_graph": analysis.get(
                "code_analysis",
                {},
            ).get(
                "module_graph",
                {},
            ),
            "parsed_files": analysis.get(
                "code_analysis",
                {},
            ).get(
                "parsed_files",
                [],
            ),
            "source_files": source_files,
        }

    def _select_source_files(self, analysis: dict) -> list[str]:
        files = analysis.get("files", [])
        available_files = set(files)
        selected = []

        def add_file(path: str):
            if not path or path in selected:
                return

            filename = Path(path).name.lower()
            extension = Path(path).suffix.lower()

            # Skip generated TypeScript declaration files
            if filename.endswith(".d.ts"):
                return

            # Prefer TypeScript source over compiled JavaScript
            if extension == ".js" and path[:-3] + ".ts" in available_files:
                return

            if (
                extension not in self.SOURCE_EXTENSIONS
                and not filename.startswith("readme")
            ):
                return

            selected.append(path)

        # Prioritize connected modules
        dependencies = analysis.get(
            "code_analysis", {}
        ).get("dependencies", [])

        for dependency in dependencies:
            if dependency.get("internal_dependencies"):
                add_file(dependency.get("file"))

            for target in dependency.get("internal_dependencies", []):
                add_file(target)

        # Include project documentation
        for path in files:
            if Path(path).name.lower().startswith("readme"):
                add_file(path)

        # Include remaining source and UI files
        for path in files:
            add_file(path)

        return selected[:self.MAX_SOURCE_FILES]

    def _read_source_file(self, relative_path: str) -> str | None:
        file_path = self.repository_path / relative_path

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return None

        if len(content) > self.MAX_FILE_CHARS:
            return (
                content[:self.MAX_FILE_CHARS]
                + "\n\n[File truncated by DevLens]"
            )

        return content