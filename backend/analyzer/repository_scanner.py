from collections import Counter
from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
}


IMPORTANT_FILES = {
    "readme.md",
    "readme",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "poetry.lock",
    "pom.xml",
    "build.gradle",
    "settings.gradle",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "tsconfig.json",
    "vite.config.js",
    "vite.config.ts",
}


class RepositoryScanner:

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Repository path does not exist: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {self.repository_path}"
            )

    def scan(self) -> dict:
        total_files = 0
        total_directories = 0

        extension_counts = Counter()

        files = []
        directories = []
        important_files = []

        for path in self.repository_path.rglob("*"):

            if self._should_ignore(path):
                continue

            relative_path = path.relative_to(self.repository_path)

            if path.is_dir():
                total_directories += 1
                directories.append(relative_path.as_posix())

            elif path.is_file():
                total_files += 1
                files.append(relative_path.as_posix())

                extension = path.suffix.lower()

                if extension:
                    extension_counts[extension] += 1

                if path.name.lower() in IMPORTANT_FILES:
                    important_files.append(relative_path.as_posix())

        return {
            "project_name": self.repository_path.name,
            "repository_path": str(self.repository_path),
            "statistics": {
                "total_files": total_files,
                "total_directories": total_directories,
                "extensions": dict(extension_counts),
            },
            "important_files": sorted(important_files),
            "directories": sorted(directories),
            "files": sorted(files),
            "top_level_structure": self._get_top_level_structure(),
        }

    def _should_ignore(self, path: Path) -> bool:
        relative_parts = path.relative_to(self.repository_path).parts

        return any(
            part in IGNORED_DIRECTORIES
            for part in relative_parts
        )

    def _get_top_level_structure(self) -> list[dict]:
        structure = []

        for item in sorted(
            self.repository_path.iterdir(),
            key=lambda path: path.name.lower()
        ):
            if item.name in IGNORED_DIRECTORIES:
                continue

            structure.append(
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                }
            )

        return structure