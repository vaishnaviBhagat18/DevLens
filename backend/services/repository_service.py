import tempfile

from git import Repo, GitCommandError

from backend.analyzer.repository_scanner import RepositoryScanner
from backend.analyzer.tech_detector import TechDetector
from backend.analyzer.parsing.tree_sitter_parser import TreeSitterParser
from backend.analyzer.dependency_extractor import DependencyExtractor
from backend.analyzer.module_graph import ModuleGraph
from backend.analyzer.context_builder import ContextBuilder
from backend.services.ai_service import AIService


class RepositoryService:

    def analyze_repository(self, repository_url: str) -> dict:
        repository_name = self._get_repository_name(repository_url)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                Repo.clone_from(repository_url, temp_dir, depth=1)
            except GitCommandError as error:
                raise ValueError(
                    f"Failed to clone repository: {error}"
                ) from error
            return self._analyze_directory(
                temp_dir, repository_name, repository_url=repository_url
            )

    def analyze_local_repository(self, repository_path: str, project_name: str) -> dict:
        """Analyze an already-extracted local directory (used for ZIP uploads)."""
        return self._analyze_directory(repository_path, project_name)

    def _analyze_directory(
        self, repository_path: str, project_name: str, repository_url: str | None = None
    ) -> dict:
        scanner = RepositoryScanner(repository_path)
        result = scanner.scan()

        tech_detector = TechDetector(
            repository_path=repository_path,
            scan_result=result,
        )
        result["technology"] = tech_detector.detect()

        parser = TreeSitterParser(repository_path)
        parsed_files = parser.parse_repository(result["files"])

        dependency_extractor = DependencyExtractor(
            repository_path=repository_path,
            repository_files=result["files"],
        )
        dependencies = []
        for parsed_file in parsed_files:
            if "error" in parsed_file:
                continue
            dependencies.append(
                dependency_extractor.extract(
                    source_file=parsed_file["file"],
                    parsed_structure=parsed_file["structure"],
                )
            )

        module_graph = ModuleGraph()
        graph = module_graph.build(
            parsed_files=parsed_files,
            dependencies=dependencies,
        )
        result["code_analysis"] = {
            "parsed_files": parsed_files,
            "dependencies": dependencies,
            "module_graph": graph,
        }
        result["project_name"] = project_name
        if repository_url:
            result["repository_url"] = repository_url
            result["source_type"] = "github"
        else:
            result["source_type"] = "zip"

        context_builder = ContextBuilder(repository_path)
        ai_context = context_builder.build(result)
        result["ai_insights"] = AIService().analyze_project(ai_context)
        result.pop("repository_path", None)
        return result

    def _get_repository_name(self, repository_url: str) -> str:
        name = repository_url.rstrip("/").split("/")[-1]
        return name[:-4] if name.endswith(".git") else name
