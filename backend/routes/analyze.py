from fastapi import APIRouter

from backend.models.schemas import AnalyzeRepositoryRequest


router = APIRouter(
    prefix="/analyze",
    tags=["Repository Analysis"],
)


@router.post("")
def analyze_repository(request: AnalyzeRepositoryRequest):
    return {
        "repository_url": request.repository_url,
        "status": "analysis_requested"
    }