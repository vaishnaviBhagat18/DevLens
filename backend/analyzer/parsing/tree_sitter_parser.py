from pathlib import Path

from tree_sitter_language_pack import get_parser
from backend.analyzer.parsing.extractors.javascript_extractor import (
    JavaScriptExtractor,
)

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
}


class TreeSitterParser:
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()
        self._parsers = {}

    def parse_file(self, relative_path: str) -> dict:
        file_path = self.repository_path / relative_path

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {relative_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Path is not a file: {relative_path}"
            )

        extension = file_path.suffix.lower()
        language = SUPPORTED_EXTENSIONS.get(extension)

        if language is None:
            raise ValueError(
                f"Unsupported source file type: {extension}"
            )

        try:
            source_code = file_path.read_bytes()
        except OSError as error:
            raise ValueError(
                f"Could not read source file: {relative_path}"
            ) from error

        parser = self._get_parser(language)
        tree = parser.parse(source_code)
        root_node = tree.root_node
        structure = self._extract_structure(
            language,
            source_code,
            root_node,
        )

        return {
            "file": relative_path,
            "language": language,
            "root_node_type": root_node.type,
            "has_errors": root_node.has_error,
            "structure": structure,
        }

    def parse_repository(self, files: list[str]) -> list[dict]:
        parsed_files = []

        for relative_path in files:
            extension = Path(relative_path).suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            try:
                result = self.parse_file(relative_path)
                parsed_files.append(result)

            except (FileNotFoundError, ValueError) as error:
                parsed_files.append(
                    {
                        "file": relative_path,
                        "error": str(error),
                    }
                )

        return parsed_files

    def _get_parser(self, language: str):
        if language not in self._parsers:
            self._parsers[language] = get_parser(language)

        return self._parsers[language]

    def _extract_structure(
        self,
        language: str,
        source_code: bytes,
        root_node,
    ) -> dict:

        if language in {
            "javascript",
            "typescript",
            "tsx",
        }:
            extractor = JavaScriptExtractor(source_code)
            return extractor.extract(root_node)

        return {
            "imports": [],
            "functions": [],
            "classes": [],
            "exports": [],
            "routes": [],
        }