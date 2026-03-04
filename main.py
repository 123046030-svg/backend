from fastapi import FastAPI
from api.mail import router as mail_router

app = FastAPI()

app.include_router(mail_router)