# modules/demo_profile/ui.py
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_db
from user_profile.models import DemoProfile
from notifications.service import enqueue_email  # tu outbox

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # .../user_profile
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/ui/profile", tags=["ui-profile"])

def _diff(old: DemoProfile, new_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Retorna una lista de cambios tipo:
    [{"field":"phone","label":"Teléfono","old":"...","new":"..."}]
    """
    mapping = {
        "full_name": "Nombre",
        "email": "Correo",
        "phone": "Teléfono",
        "department": "Área/Departamento",
    }
    changes = []
    for field, label in mapping.items():
        old_val = getattr(old, field, None)
        new_val = new_data.get(field)
        # normaliza None/""
        old_s = "" if old_val is None else str(old_val)
        new_s = "" if new_val is None else str(new_val)
        if old_s != new_s:
            changes.append({"field": field, "label": label, "old": old_s, "new": new_s})
    return changes

@router.get("/edit", response_class=HTMLResponse)
async def edit_profile(request: Request, db: AsyncSession = Depends(get_db)):
    # simulamos usuario logueado id=1
    user_id = 1
    res = await db.execute(select(DemoProfile).where(DemoProfile.id == user_id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "DemoProfile not found. Inserta el registro id=1 en DB.")
    return templates.TemplateResponse(
        "ui/profile_edit.html",
        {"request": request, "profile": profile, "message": None},
    )

@router.post("/edit")
async def edit_profile_post(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    user_id = 1

    res = await db.execute(select(DemoProfile).where(DemoProfile.id == user_id))
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "DemoProfile not found.")

    new_data = {
        "full_name": full_name.strip(),
        "email": email.strip(),
        "phone": (phone or "").strip() or None,
        "department": (department or "").strip() or None,
    }

    changes = _diff(profile, new_data)

    # aplica cambios
    profile.full_name = new_data["full_name"]
    profile.email = new_data["email"]
    profile.phone = new_data["phone"]
    profile.department = new_data["department"]
    profile.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(profile)

    # Encolar correo con resumen
    # Destino: el mismo usuario (profile.email) + opcional CC a auditoría
    recipients = [profile.email]

    context = {
        "full_name": profile.full_name,
        "email": profile.email,
        "updated_at": profile.updated_at.isoformat(),
        "changes": changes,
        "has_changes": bool(changes),
    }

    outbox = await enqueue_email(
        db=db,
        recipients=recipients,
        subject="Resumen de actualización de perfil",
        template_name="email/profile_update_summary.html",
        context=context,
        body_html=None,
        source_module="demo_profile",
        created_by_user_id=user_id,
    )

    # Redirige a la misma vista con mensaje
    return RedirectResponse(url=f"/ui/profile/edit?queued={outbox.id}", status_code=303)