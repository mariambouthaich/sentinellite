from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import auth, events
from app.core.database import get_db

app = FastAPI(
    title="SentinelLite API",
    description="Application de détection d'activités suspectes",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(events.router)


@app.get("/")
def accueil():
    return {"projet": "SentinelLite", "message": "Bienvenue sur l'API de SentinelLite"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Vérifie que l'API ET la base de données répondent."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
