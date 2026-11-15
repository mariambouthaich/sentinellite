from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventOut, EventPage, ImportResult
from app.services.importer import CsvFormatError, parse_csv

router = APIRouter(prefix="/events", tags=["events"])

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 Mo


def _key(ts: datetime, ip: str, user: str, etype: str, st: str) -> tuple:
    """Clé de déduplication (horodatage normalisé en UTC, sans fuseau)."""
    if ts.tzinfo is not None:
        ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
    return (ts, ip, user, etype, st)


@router.post("/import", response_model=ImportResult)
async def import_events(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Seuls les fichiers .csv sont acceptés")

    content = await file.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Fichier trop volumineux (5 Mo max)")

    try:
        parsed = parse_csv(content)
    except CsvFormatError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

    # Déduplication : on ignore les événements déjà présents en base
    existing: set[tuple] = set()
    if parsed.events:
        lo = min(e["timestamp"] for e in parsed.events)
        hi = max(e["timestamp"] for e in parsed.events)
        rows = db.execute(
            select(Event.timestamp, Event.source_ip, Event.username, Event.event_type, Event.status)
            .where(Event.timestamp >= lo, Event.timestamp <= hi)
        ).all()
        existing = {_key(*r) for r in rows}

    new_events, duplicates = [], 0
    for e in parsed.events:
        k = _key(e["timestamp"], e["source_ip"], e["username"], e["event_type"], e["status"])
        if k in existing:
            duplicates += 1
        else:
            existing.add(k)  # évite aussi les doublons à l'intérieur du fichier
            new_events.append(Event(**e))

    db.add_all(new_events)
    db.add(AuditLog(user_id=admin.id, action="events_import", target_type="file", target_id=(file.filename or "")[:50]))
    db.commit()

    return ImportResult(
        inserted=len(new_events), duplicates=duplicates, rejected=parsed.rejected, errors=parsed.errors
    )


@router.get("", response_model=EventPage)
def list_events(
    username: str | None = None,
    source_ip: str | None = None,
    event_type: str | None = None,
    event_status: str | None = Query(None, alias="status"),
    start: datetime | None = None,
    end: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(Event)
    if username:
        query = query.where(Event.username == username)
    if source_ip:
        query = query.where(Event.source_ip == source_ip)
    if event_type:
        query = query.where(Event.event_type == event_type)
    if event_status:
        query = query.where(Event.status == event_status)
    if start:
        query = query.where(Event.timestamp >= start)
    if end:
        query = query.where(Event.timestamp <= end)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(
        query.order_by(Event.timestamp.desc(), Event.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return EventPage(items=items, total=total, page=page, page_size=page_size)
