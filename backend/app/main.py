from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="QuizVeda API — implementation scaffold",
)


@app.get("/health/live", tags=["platform"])
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["platform"])
async def readiness() -> dict[str, str]:
    # Database connectivity check is added with the persistence milestone.
    return {"status": "ready", "database": "not_checked"}


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs"}
