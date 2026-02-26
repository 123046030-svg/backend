from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import logging

from services.mailer import Mailer
from core.settings import settings  # ajusta si tu ruta real es distinta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


def get_mailer() -> Mailer:
    return Mailer()


class EmailRequest(BaseModel):
    recipients: Optional[List[EmailStr]] = None
    subject: str = "FastAPI-Mail test"
    body: Dict[str, Any] = {}


@router.post("/test")
async def send_test(
    payload: EmailRequest,
    background_tasks: BackgroundTasks,
    mailer: Mailer = Depends(get_mailer),
):
    recipients = [str(x) for x in (payload.recipients or [])]

    # fallback a destinatario de prueba si no mandan recipients
    if not recipients:
        test_recipient = getattr(settings, "MAIL_TEST_RECIPIENT", None)
        if test_recipient:
            recipients = [str(test_recipient)]

    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No recipients provided and MAIL_TEST_RECIPIENT is not configured.",
        )

    try:
        await mailer.send_template(
            subject=payload.subject,
            recipients=recipients,
            template_name="email/test_email.html",
            context=payload.body,
            background_tasks=background_tasks,
        )
        return {"message": "email queued", "recipients": recipients}
    except Exception as e:
        logger.exception("Error sending email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {type(e).__name__}",
        )