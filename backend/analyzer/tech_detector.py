import json
from pathlib import Path


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C/C++",
    ".hpp": "C++",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
}


class TechDetector:

    def __init__(self, repository_path: str, scan_result: dict):
        self.repository_path = Path(repository_path).resolve()
        self.scan_result = scan_result

    def detect(self) -> dict:
        return {
            "languages": self._detect_languages(),
            "frameworks": self._detect_frameworks(),
            "package_managers": self._detect_package_managers(),
            "databases": self._detect_databases(),
        }

    def _detect_languages(self) -> list[dict]:
        detected_languages = {}

        extensions = self.scan_result["statistics"]["extensions"]

        for extension, count in extensions.items():
            language = LANGUAGE_EXTENSIONS.get(extension)

            if not language:
                continue

            if language not in detected_languages:
                detected_languages[language] = {
                    "name": language,
                    "files": 0,
                    "evidence": [],
                }

            detected_languages[language]["files"] += count
            detected_languages[language]["evidence"].append(extension)

        return sorted(
            detected_languages.values(),
            key=lambda item: item["files"],
            reverse=True,
        )

    def _detect_frameworks(self) -> list[dict]:
        detected = []

        framework_dependencies = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "react": "React",
            "next": "Next.js",
            "express": "Express.js",
            "vue": "Vue.js",
            "angular": "AngularJS",
            "@angular/core": "Angular",
        }

        # Detect frameworks from package.json dependencies
        for relative_path in self.scan_result["files"]:
            filename = Path(relative_path).name.lower()

            if filename == "package.json":
                dependencies = self._read_package_json_dependencies(
                    relative_path
                )

                for dependency, framework in framework_dependencies.items():
                    if dependency in dependencies:
                        detected.append(
                            {
                                "name": framework,
                                "evidence": [relative_path],
                            }
                        )

        # Detect Python frameworks from Python dependency files
        python_frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
        }

        for relative_path in self.scan_result["files"]:
            filename = Path(relative_path).name.lower()

            if filename not in {
                "requirements.txt",
                "pyproject.toml",
            }:
                continue

            content = self._read_file(relative_path)

            if content is None:
                continue

            content_lower = content.lower()

            for dependency, framework in python_frameworks.items():
                if dependency in content_lower:
                    detected.append(
                        {
                            "name": framework,
                            "evidence": [relative_path],
                        }
                    )

        return self._merge_detections(detected)

    def _detect_package_managers(self) -> list[dict]:
        files = self.scan_result["files"]

        detected = []

        package_json_files = [
            path for path in files
            if Path(path).name.lower() == "package.json"
        ]

        npm_files = [
            path for path in files
            if Path(path).name.lower() == "package-lock.json"
        ]

        yarn_files = [
            path for path in files
            if Path(path).name.lower() == "yarn.lock"
        ]

        pnpm_files = [
            path for path in files
            if Path(path).name.lower() == "pnpm-lock.yaml"
        ]

        if npm_files:
            detected.append(
                {
                    "name": "npm",
                    "evidence": package_json_files + npm_files,
                }
            )

        if yarn_files:
            detected.append(
                {
                    "name": "Yarn",
                    "evidence": package_json_files + yarn_files,
                }
            )

        if pnpm_files:
            detected.append(
                {
                    "name": "pnpm",
                    "evidence": package_json_files + pnpm_files,
                }
            )

        for relative_path in files:
            filename = Path(relative_path).name.lower()

            if filename == "requirements.txt":
                detected.append(
                    {
                        "name": "pip",
                        "evidence": [relative_path],
                    }
                )

            elif filename == "pipfile":
                detected.append(
                    {
                        "name": "Pipenv",
                        "evidence": [relative_path],
                    }
                )

            elif filename == "poetry.lock":
                detected.append(
                    {
                        "name": "Poetry",
                        "evidence": [relative_path],
                    }
                )

            elif filename == "pom.xml":
                detected.append(
                    {
                        "name": "Maven",
                        "evidence": [relative_path],
                    }
                )

            elif filename in {"build.gradle", "build.gradle.kts"}:
                detected.append(
                    {
                        "name": "Gradle",
                        "evidence": [relative_path],
                    }
                )

        return self._merge_detections(detected)

    def _detect_databases(self) -> list[dict]:
        detected = []

        database_dependencies = {
            "mongoose": "MongoDB",
            "mongodb": "MongoDB",
            "pg": "PostgreSQL",
            "postgres": "PostgreSQL",
            "mysql": "MySQL",
            "mysql2": "MySQL",
            "sqlite3": "SQLite",
            "redis": "Redis",
        }

        # Detect databases from package.json
        for relative_path in self.scan_result["files"]:
            filename = Path(relative_path).name.lower()

            if filename == "package.json":
                dependencies = self._read_package_json_dependencies(
                    relative_path
                )

                for dependency, database in database_dependencies.items():
                    if dependency in dependencies:
                        detected.append(
                            {
                                "name": database,
                                "evidence": [relative_path],
                            }
                        )

        # Detect databases from Python dependency files
        python_database_indicators = {
            "psycopg": "PostgreSQL",
            "psycopg2": "PostgreSQL",
            "pymysql": "MySQL",
            "mysql-connector": "MySQL",
            "pymongo": "MongoDB",
            "sqlite": "SQLite",
            "redis": "Redis",
        }

        for relative_path in self.scan_result["files"]:
            filename = Path(relative_path).name.lower()

            if filename not in {
                "requirements.txt",
                "pyproject.toml",
            }:
                continue

            content = self._read_file(relative_path)

            if content is None:
                continue

            content_lower = content.lower()

            for indicator, database in python_database_indicators.items():
                if indicator in content_lower:
                    detected.append(
                        {
                            "name": database,
                            "evidence": [relative_path],
                        }
                    )

        # Docker Compose may directly declare database services
        docker_database_indicators = {
            "postgres": "PostgreSQL",
            "mysql": "MySQL",
            "mongo": "MongoDB",
            "redis": "Redis",
        }

        for relative_path in self.scan_result["files"]:
            filename = Path(relative_path).name.lower()

            if filename not in {
                "docker-compose.yml",
                "docker-compose.yaml",
            }:
                continue

            content = self._read_file(relative_path)

            if content is None:
                continue

            content_lower = content.lower()

            for indicator, database in docker_database_indicators.items():
                if indicator in content_lower:
                    detected.append(
                        {
                            "name": database,
                            "evidence": [relative_path],
                        }
                    )

        return self._merge_detections(detected)

    def _read_package_json_dependencies(
        self,
        relative_path: str
    ) -> set[str]:

        file_path = self.repository_path / relative_path

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError):
            return set()

        dependencies = set()

        for section in (
            "dependencies",
            "devDependencies",
            "peerDependencies",
        ):
            section_dependencies = data.get(section, {})

            if isinstance(section_dependencies, dict):
                dependencies.update(
                    dependency.lower()
                    for dependency in section_dependencies.keys()
                )

        return dependencies

    def _read_file(self, relative_path: str) -> str | None:
        file_path = self.repository_path / relative_path

        try:
            return file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        except (OSError, UnicodeError):
            return None

    def _merge_detections(
        self,
        detections: list[dict]
    ) -> list[dict]:

        merged = {}

        for detection in detections:
            name = detection["name"]

            if name not in merged:
                merged[name] = {
                    "name": name,
                    "evidence": [],
                }

            for evidence in detection["evidence"]:
                if evidence not in merged[name]["evidence"]:
                    merged[name]["evidence"].append(evidence)

        return list(merged.values())