import logging

from fastapi import FastAPI

from app.api import auth, users, animals, catalog, weightings, admin

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(animals.router)
app.include_router(catalog.router)
app.include_router(weightings.router)
app.include_router(admin.router)

@app.get("/health")
def health():
    return {"status": "ok"}