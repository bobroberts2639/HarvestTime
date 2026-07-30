"""Harvest Time — FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.modules.fields import router as fields_router
from app.modules.weather import router as weather_router
from app.modules.recommendations import router as recommendations_router
from app.modules.notes import router as notes_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Smart farming advisor — weather intelligence meets agronomic science",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


# Register module routers
app.include_router(fields_router)
app.include_router(weather_router)
app.include_router(recommendations_router)
app.include_router(notes_router)
