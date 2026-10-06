import tempfile

from git import Repo, GitCommandError

from backend.analyzer.repository_scanner import RepositoryScanner
from backend.analyzer.tech_detector import TechDetector
from backend.analyzer.parsing.tree_sitter_parser import TreeSitterParser
from backend.analyzer.dependency_extractor import DependencyExtractor
from backend.analyzer.module_graph import ModuleGraph


class RepositoryService:

    def analyze_repository(self, repository_url: str) -> dict:
        repository_name = self._get_repository_name(repository_url)

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                Repo.clone_from(
                    repository_url,
                    temp_dir,
                    depth=1,
                )
            except GitCommandError as error:
                raise ValueError(
                    f"Failed to clone repository: {error}"
                ) from error

            # 1. Scan repository
            scanner = RepositoryScanner(temp_dir)
            result = scanner.scan()

            # 2. Detect technologies
            tech_detector = TechDetector(
                repository_path=temp_dir,
                scan_result=result,
            )

            result["technology"] = tech_detector.detect()

            # 3. Parse source files
            parser = TreeSitterParser(temp_dir)

            parsed_files = parser.parse_repository(
                result["files"]
            )

            # 4. Extract dependencies
            dependency_extractor = DependencyExtractor(
                repository_path=temp_dir,
                repository_files=result["files"],
            )

            dependencies = []

            for parsed_file in parsed_files:
                if "error" in parsed_file:
                    continue

                dependency_result = dependency_extractor.extract(
                    source_file=parsed_file["file"],
                    parsed_structure=parsed_file["structure"],
                )

                dependencies.append(dependency_result)

            # 5. Build module graph
            module_graph = ModuleGraph()

            graph = module_graph.build(
                parsed_files=parsed_files,
                dependencies=dependencies,
            )

            # 6. Add code analysis to response
            result["code_analysis"] = {
                "parsed_files": parsed_files,
                "dependencies": dependencies,
                "module_graph": graph,
            }

            # Public repository information
            result["project_name"] = repository_name
            result["repository_url"] = repository_url

            # Do not expose temporary server path
            result.pop("repository_path", None)

            return result

    def _get_repository_name(self, repository_url: str) -> str:
        name = repository_url.rstrip("/").split("/")[-1]

        if name.endswith(".git"):
            name = name[:-4]

        return name