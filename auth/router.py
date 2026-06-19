import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.segurity import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


@router.post("/token")
async def generate_token(payload: TokenRequest):
    expected_client_id = 1
    expected_client_secret = "P4QdI5vjFusOko5JxkjCyG"

    if (
        payload.client_id != expected_client_id
        or payload.client_secret != expected_client_secret
    ):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({
        "sub": payload.client_id,
        "scope": "mailer:use",
    })

    return {
        "access_token": token,
        "token_type": "bearer",
    }