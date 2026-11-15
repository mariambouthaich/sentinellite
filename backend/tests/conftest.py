import os

# Base temporaire pour les tests : doit être définie AVANT d'importer l'app
os.environ["DATABASE_URL"] = "sqlite:///./test_sentinellite.db"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.main import app
from app.models.user import User


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(User(email="admin@test.local", password_hash=hash_password("AdminPass123"), role="admin"))
        db.add(User(email="analyst@test.local", password_hash=hash_password("AnalystPass123"), role="analyst"))
        db.commit()
    yield TestClient(app)
    Base.metadata.drop_all(engine)


def login(client, email, password):
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client):
    return login(client, "admin@test.local", "AdminPass123")


@pytest.fixture()
def analyst_headers(client):
    return login(client, "analyst@test.local", "AnalystPass123")