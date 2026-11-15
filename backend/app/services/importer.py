"""Lecture et validation d'un fichier CSV d'événements."""
import csv
import io
import ipaddress
from dataclasses import dataclass, field
from datetime import datetime, timezone

REQUIRED_COLUMNS = {"timestamp", "source_ip", "username", "event_type", "status", "source"}
VALID_STATUS = {"success", "failure"}
MAX_ROWS = 50_000
MAX_ERRORS_SHOWN = 20


@dataclass
class ParseResult:
    events: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    rejected: int = 0


class CsvFormatError(ValueError):
    """Le fichier entier est inutilisable (pas du CSV, colonnes manquantes...)."""


def _parse_timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_csv(content: bytes) -> ParseResult:
    try:
        text = content.decode("utf-8-sig")  # accepte aussi le BOM d'Excel
    except UnicodeDecodeError:
        raise CsvFormatError("Le fichier doit être encodé en UTF-8.")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise CsvFormatError("Fichier vide.")
    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        raise CsvFormatError(f"Colonnes manquantes : {', '.join(sorted(missing))}")

    result = ParseResult()
    for line_no, row in enumerate(reader, start=2):  # ligne 1 = en-tête
        if line_no - 1 > MAX_ROWS:
            raise CsvFormatError(f"Trop de lignes (maximum {MAX_ROWS}).")
        try:
            event = {
                "timestamp": _parse_timestamp(row["timestamp"]),
                "source_ip": str(ipaddress.ip_address(row["source_ip"].strip())),
                "username": row["username"].strip(),
                "event_type": row["event_type"].strip(),
                "status": row["status"].strip().lower(),
                "source": row["source"].strip(),
            }
            if event["status"] not in VALID_STATUS:
                raise ValueError(f"status doit valoir success ou failure (reçu : {row['status']!r})")
            if not event["username"] or len(event["username"]) > 100:
                raise ValueError("username vide ou trop long")
            if not event["event_type"] or len(event["event_type"]) > 50:
                raise ValueError("event_type vide ou trop long")
            if not event["source"] or len(event["source"]) > 100:
                raise ValueError("source vide ou trop long")
            result.events.append(event)
        except (ValueError, AttributeError, TypeError) as exc:
            result.rejected += 1
            if len(result.errors) < MAX_ERRORS_SHOWN:
                result.errors.append(f"Ligne {line_no} : {exc}")
    return result
