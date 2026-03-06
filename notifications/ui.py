# modules/notifications/ui.py
import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.db import get_db  # tu dependencia
from .service import enqueue_email

templates = Jinja2Templates(directory="modules/notifications/templates")

router = APIRouter(prefix="/notifications/email", tags=["notifications-ui"])

@router.get("/new", response_class=HTMLResponse)
async def email_new(request: Request):
    return templates.TemplateResponse("notifications/email_new.html", {"request": request})

@router.post("/new")
async def email_new_post(
    request: Request,
    to: str = Form(...),
    subject: str = Form(...),
    template_name: str = Form("email/test_email.html"),
    context_json: str = Form("{}"),
    source_module: str = Form("manual-ui"),
    db: AsyncSession = Depends(get_db),
):
    recipients = [x.strip() for x in to.split(",") if x.strip()]
    context = json.loads(context_json or "{}")

    row = await enqueue_email(
        db,
        recipients=recipients,
        subject=subject,
        template_name=template_name or None,
        context=context,
        body_html=None,
        source_module=source_module,
        created_by_user_id=None,  # aquí conecta tu auth cuando esté
    )
    return RedirectResponse(url=f"/notifications/email/{row.id}", status_code=303)