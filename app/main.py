from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_v1
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.project_name, version=settings.app_version)
app.include_router(api_v1, prefix="/api/v1")

allow_origins = [o.strip() for o in settings.allow_origins.split(",") if o.strip()]
print(f"Allowing origins: {allow_origins}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # exact origins only if using credentials
    allow_credentials=False,  # set False if you don't need cookies/auth
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # or list specific: ["Authorization","Content-Type"]
    expose_headers=["*"],  # optional
    max_age=86400,  # cache preflight for 1 day
)


@app.get("/info")
async def info() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "env": settings.env,
            "app_name": settings.project_name,
            "app_version": settings.app_version,
        }
    )
