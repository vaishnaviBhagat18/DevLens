from pydantic import BaseModel, HttpUrl


class AnalyzeRepositoryRequest(BaseModel):
    repository_url: HttpUrl

    