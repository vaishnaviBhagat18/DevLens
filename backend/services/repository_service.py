import tempfile

from git import Repo, GitCommandError

from backend.analyzer.repository_scanner import RepositoryScanner
from backend.analyzer.tech_detector import TechDetector

class RepositoryService:

    def analyze_repository(self, repository_url: str) -> dict:

        repository_name = self._get_repository_name(repository_url)

        with tempfile.TemporaryDirectory() as temp_dir:

            try:
                Repo.clone_from(
                    repository_url,
                    temp_dir,
                    depth=1
                )

            except GitCommandError as error:
                raise ValueError(
                    f"Failed to clone repository: {error}"
                ) from error

            scanner = RepositoryScanner(temp_dir)
            result = scanner.scan()

            tech_detector = TechDetector(
                repository_path=temp_dir,
                scan_result=result,
            )

            technology = tech_detector.detect()

            result["project_name"] = repository_name
            result["repository_url"] = repository_url
            result["technology"] = technology

            # Do not expose our server's temporary filesystem path
            result.pop("repository_path", None)

            return result

    def _get_repository_name(self, repository_url: str) -> str:
        name = repository_url.rstrip("/").split("/")[-1]

        if name.endswith(".git"):
            name = name[:-4]

        return name