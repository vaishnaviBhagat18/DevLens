from pathlib import Path


class DependencyExtractor:

    RESOLVABLE_EXTENSIONS = [
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".py",
    ]

    def __init__(self, repository_path: str, repository_files: list[str]):
        self.repository_path = Path(repository_path).resolve()

        self.repository_files = {
            self._normalize_path(path)
            for path in repository_files
        }

    def extract(
        self,
        source_file: str,
        parsed_structure: dict,
    ) -> dict:

        internal_dependencies = []
        external_dependencies = []
        unresolved_dependencies = []

        for import_data in parsed_structure.get("imports", []):
            import_source = import_data.get("source")

            if not import_source:
                continue

            if self._is_relative_import(import_source):
                resolved = self._resolve_relative_import(
                    source_file,
                    import_source,
                )

                if resolved:
                    if resolved not in internal_dependencies:
                        internal_dependencies.append(resolved)
                else:
                    if import_source not in unresolved_dependencies:
                        unresolved_dependencies.append(import_source)

            else:
                package_name = self._get_package_name(import_source)

                if package_name not in external_dependencies:
                    external_dependencies.append(package_name)

        return {
            "file": self._normalize_path(source_file),
            "internal_dependencies": internal_dependencies,
            "external_dependencies": external_dependencies,
            "unresolved_dependencies": unresolved_dependencies,
        }

    def _is_relative_import(self, import_source: str) -> bool:
        return (
            import_source.startswith("./")
            or import_source.startswith("../")
        )

    def _resolve_relative_import(
        self,
        source_file: str,
        import_source: str,
    ) -> str | None:

        source_path = Path(
            self._normalize_path(source_file)
        )

        source_directory = source_path.parent

        import_path = (
            source_directory / import_source
        )

        normalized_import = self._normalize_path(
            str(import_path)
        )

        # Exact file reference
        if normalized_import in self.repository_files:
            return normalized_import

        # Example:
        # ./models/Slot -> ./models/Slot.js
        for extension in self.RESOLVABLE_EXTENSIONS:
            candidate = normalized_import + extension

            if candidate in self.repository_files:
                return candidate

        # Example:
        # ./routes -> ./routes/index.js
        for extension in self.RESOLVABLE_EXTENSIONS:
            candidate = self._normalize_path(
                str(Path(normalized_import) / f"index{extension}")
            )

            if candidate in self.repository_files:
                return candidate

        return None

    def _get_package_name(self, import_source: str) -> str:
        parts = import_source.split("/")

        # Scoped npm package:
        # @angular/core -> @angular/core
        if import_source.startswith("@") and len(parts) >= 2:
            return "/".join(parts[:2])

        # Normal package:
        # express -> express
        # lodash/map -> lodash
        return parts[0]

    def _normalize_path(self, path: str) -> str:
        return Path(path).as_posix()