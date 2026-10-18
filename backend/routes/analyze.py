import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.models.schemas import AnalyzeRepositoryRequest
from backend.services.archive_service import ArchiveService
from backend.services.repository_service import RepositoryService

router = APIRouter(prefix="/analyze", tags=["Repository Analysis"])
repository_service = RepositoryService()
archive_service = ArchiveService()


@router.post("")
def analyze_repository(request: AnalyzeRepositoryRequest):
    try:
        return repository_service.analyze_repository(str(request.repository_url))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/upload")
def analyze_uploaded_zip(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a .zip project archive.")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_root = archive_service.extract_zip(file.file, temp_dir)
            project_name = Path(filename.replace("\\", "/")).stem
            return repository_service.analyze_local_repository(
                str(extracted_root), project_name=project_name
            )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        file.file.close()
