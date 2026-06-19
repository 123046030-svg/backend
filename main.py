from fastapi import FastAPI

from auth.router import router as auth_router
from user_profile.ui import router as profile_ui_router


app = FastAPI(title="Demo Notifications")

app.include_router(auth_router)
app.include_router(profile_ui_router)