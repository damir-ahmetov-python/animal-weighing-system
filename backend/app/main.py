import logging

from fastapi import FastAPI

from app.api import auth, users

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/health")
def health():
    return {"status": "ok"}