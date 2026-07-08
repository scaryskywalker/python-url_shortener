from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.core.config import get_settings
from app.routes.config_routes import router as config_router
from app.routes.health_routes import router as health_router
from app.routes.merchant_routes import router as merchant_router
from app.routes.strategy_routes import router as strategy_router
from app.routes.url_routes import api_router as url_api_router
from app.routes.url_routes import public_router as url_public_router

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend-only merchant URL shortener with MySQL, Redis, API key authentication, and Alembic.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(merchant_router)
app.include_router(strategy_router)
app.include_router(config_router)
app.include_router(url_api_router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard_home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(url_public_router)
