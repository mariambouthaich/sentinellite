
# Il décrit la table events, qui correspond aux lignes de ton sample_logs.csv (mêmes colonnes).
from backend.app.core.database import Base
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(100))
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True) #extra accepte des informations supplémentaires en JSON