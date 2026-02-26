from typing import Any, Dict, List
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr

from services.mailer import Mailer

router = APIRouter(prefix="/email", tags=["email"])

def get_mailer() -> Mailer:
    return Mailer()

class EmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str = "FastAPI-Mail test"
    body: Dict[str, Any] = {}

@router.post("/test")
async def send_test(
    payload: EmailRequest,
    background_tasks: BackgroundTasks,
    mailer: Mailer = Depends(get_mailer),
):
    # manda template
    await mailer.send_template(
        subject=payload.subject,
        recipients=[str(x) for x in payload.recipients],
        template_name="email/test_email.html",
        context=payload.body,
        background_tasks=background_tasks,
    )
    return {"message": "email queued"}