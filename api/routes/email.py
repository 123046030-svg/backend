from typing import Any, Dict, List, Optional

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.mail import conf
from services.mailer import Mailer
from core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


def get_mailer() -> Mailer:
    return Mailer()


class EmailRequest(BaseModel):
    recipients: Optional[List[EmailStr]] = None
    subject: str = "Prueba de correo con Brevo"
    body: Dict[str, Any] = Field(default_factory=dict)


@router.get("/test")
async def send_test_email():
    try:
        message = MessageSchema(
            subject="Prueba de correo con Brevo",
            recipients=[settings.MAIL_TEST_RECIPIENT],
            body="""
            <h2>Hola</h2>
            <p>Este es un correo de prueba enviado desde FastAPI usando Brevo SMTP.</p>
            """,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        return {
            "ok": True,
            "message": "Correo enviado correctamente",
            "recipient": settings.MAIL_TEST_RECIPIENT,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {type(e).__name__}: {str(e)}",
        )


@router.post("/test-template")
async def send_test_template(
    payload: EmailRequest,
    background_tasks: BackgroundTasks,
    mailer: Mailer = Depends(get_mailer),
):
    """
    Prueba usando plantilla HTML.
    Si no mandas recipients, usa MAIL_TEST_RECIPIENT.
    """
    recipients = [str(x) for x in (payload.recipients or [])]

    if not recipients:
        test_recipient = getattr(settings, "MAIL_TEST_RECIPIENT", None)
        if test_recipient:
            recipients = [str(test_recipient)]

    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron recipients y MAIL_TEST_RECIPIENT no está configurado.",
        )

    context = payload.body or {
        "nombre": "Regina",
        "mensaje": "Este es un correo de prueba enviado con plantilla desde FastAPI y Brevo.",
    }

    try:
        await mailer.send_template(
            subject=payload.subject,
            recipients=recipients,
            template_name="email/test_email.html",
            context=context,
            background_tasks=background_tasks,
        )
        return {
            "ok": True,
            "message": "Correo con plantilla enviado/encolado correctamente",
            "recipients": recipients,
        }
    except Exception as e:
        logger.exception("Error sending template email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {type(e).__name__}: {str(e)}",
        )