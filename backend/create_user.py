"""Crée un utilisateur. Usage (depuis backend/, venv activé) :
    python create_user.py admin@sentinel.local MotDePasseSolide admin
Rôles : admin | analyst
"""
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

if len(sys.argv) != 4 or sys.argv[3] not in ("admin", "analyst"):
    sys.exit(__doc__)

email, password, role = sys.argv[1:]
if len(password) < 8:
    sys.exit("Mot de passe trop court (8 caractères minimum).")

with SessionLocal() as db:
    if db.scalar(select(User).where(User.email == email)):
        sys.exit(f"{email} existe déjà.")
    db.add(User(email=email, password_hash=hash_password(password), role=role))
    db.commit()
    print(f"Utilisateur {email} créé avec le rôle {role}.")