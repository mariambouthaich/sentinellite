from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.auth import Token, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Le champ "username" du formulaire contient l'email
    user = db.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.password_hash):
        db.add(AuditLog(user_id=None, action="login_failed", target_type="user", target_id=form.username[:50]))
        db.commit()
        # même message dans les deux cas : on ne révèle pas si l'email existe
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    db.add(AuditLog(user_id=user.id, action="login_success", target_type="user", target_id=str(user.id)))
    db.commit()
    return Token(access_token=create_access_token(user.id, user.role))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
