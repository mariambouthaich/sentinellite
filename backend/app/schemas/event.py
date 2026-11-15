from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    source_ip: str
    username: str
    event_type: str
    status: str
    source: str


class EventPage(BaseModel):
    items: list[EventOut]
    total: int
    page: int
    page_size: int


class ImportResult(BaseModel):
    inserted: int
    duplicates: int
    rejected: int
    errors: list[str]  # les 20 premières erreurs, avec le numéro de ligne
