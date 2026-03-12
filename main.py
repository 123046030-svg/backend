from fastapi import FastAPI
from user_profile.ui import router as profile_ui_router

app = FastAPI(title="Demo Notifications")

app.include_router(profile_ui_router)