import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["email"])


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str = "ADS Session Summary"
    body: str = "<p>Please find your ADS session summary attached.</p>"
    pdf_base64: str
    pdf_filename: str = "ads-session-summary.pdf"


@router.post("/api/send-email")
async def send_email(request: SendEmailRequest) -> dict[str, str]:
    """Send session summary PDF via Azure Logic App (Office 365 Outlook)."""

    if not settings.logic_app_trigger_url:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. LOGIC_APP_TRIGGER_URL is not set.",
        )

    payload = {
        "to": request.to,
        "subject": request.subject,
        "body": request.body,
        "Attachments": [
            {
                "Name": request.pdf_filename,
                "ContentBytes": request.pdf_base64,
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.logic_app_trigger_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error("Logic App request timed out")
        raise HTTPException(status_code=504, detail="Email service timed out.")
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Logic App returned %s: %s", exc.response.status_code, exc.response.text
        )
        raise HTTPException(
            status_code=502,
            detail=f"Email service error: {exc.response.status_code}",
        )
    except httpx.HTTPError as exc:
        logger.error("Logic App request failed: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach email service.")

    return {"status": "sent", "to": request.to}
