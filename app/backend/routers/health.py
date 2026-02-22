from fastapi import APIRouter

from app.backend.services.session_manager import session_manager

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "active_sessions": session_manager.active_session_count,
    }
