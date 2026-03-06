from fastapi import FastAPI
from api.routes.email import router as mail_router
from user_profile.ui import router as profile_ui_router

app = FastAPI()

app.include_router(mail_router)
app.include_router(profile_ui_router)