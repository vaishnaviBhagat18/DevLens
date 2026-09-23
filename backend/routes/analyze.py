from fastapi import APIRouter, HTTPException

from backend.models.schemas import AnalyzeRepositoryRequest
from backend.services.repository_service import RepositoryService


router = APIRouter(
    prefix="/analyze",
    tags=["Repository Analysis"],
)

repository_service = RepositoryService()


@router.post("")
def analyze_repository(request: AnalyzeRepositoryRequest):

    try:
        result = repository_service.analyze_repository(
            str(request.repository_url)
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error