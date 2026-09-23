from fastapi import FastAPI

from backend.routes.analyze import router as analyze_router


app = FastAPI(
    title="DevLens API",
    description="Backend API for repository analysis and software project understanding.",
    version="0.1.0",
)

app.include_router(analyze_router)


@app.get("/")
def root():
    return {
        "name": "DevLens API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
