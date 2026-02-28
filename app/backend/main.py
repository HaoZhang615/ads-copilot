import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.config import settings
from app.backend.routers import email, health, ws
from app.backend.services.session_manager import session_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting session manager")
    await session_manager.start()
    yield
    logger.info("Shutting down — cleaning up all sessions")
    await session_manager.cleanup_all()


app = FastAPI(
    title="Databricks ADS Voice Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ws.router)
app.include_router(email.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
