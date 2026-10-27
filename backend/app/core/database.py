#Il gère la connexion à PostgreSQL et contient trois éléments :
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
#la connexion à la base (pool_pre_ping vérifie qu’elle est vivante avant de s’en servir).
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
#la classe dont héritent tous les modèles, pour que SQLAlchemy les connaisse.
class Base(DeclarativeBase):
    pass
#ouvre une session pour chaque requête HTTP, puis la ferme proprement, même en cas d’erreur.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()