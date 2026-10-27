#le point d’entrée de l’API : il crée l’application et déclare les routes
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI(
    title="SentinelLite API",
    description="Application de détection d'activités suspectes",
    version="0.1.0",
)

@app.get("/")
def accueil():
    return {"projet": "SentinelLite", "message": "Bienvenue sur l'API de SentinelLite"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}