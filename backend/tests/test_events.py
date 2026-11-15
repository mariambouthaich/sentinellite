from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample_logs.csv"
HEADER = "timestamp,source_ip,username,event_type,status,source\n"


def upload(client, headers, content, name="logs.csv"):
    return client.post("/events/import", headers=headers, files={"file": (name, content, "text/csv")})


def test_import_sample_file(client, admin_headers):
    r = upload(client, admin_headers, SAMPLE.read_bytes())
    assert r.status_code == 200
    assert r.json() == {"inserted": 219, "duplicates": 0, "rejected": 0, "errors": []}


def test_reimport_creates_no_duplicates(client, admin_headers):
    upload(client, admin_headers, SAMPLE.read_bytes())
    r = upload(client, admin_headers, SAMPLE.read_bytes())
    assert r.json()["inserted"] == 0
    assert r.json()["duplicates"] == 219


def test_invalid_rows_are_reported(client, admin_headers):
    csv_text = HEADER + (
        "2026-10-24T08:00:00Z,192.0.2.1,alice,login_success,success,test\n"
        "pas-une-date,192.0.2.1,alice,login_success,success,test\n"
        "2026-10-24T08:01:00Z,999.1.1.1,alice,login_success,success,test\n"
        "2026-10-24T08:02:00Z,192.0.2.1,alice,login_success,peut-etre,test\n"
    )
    r = upload(client, admin_headers, csv_text.encode())
    body = r.json()
    assert body["inserted"] == 1 and body["rejected"] == 3
    assert body["errors"][0].startswith("Ligne 3")


def test_missing_columns_rejected(client, admin_headers):
    r = upload(client, admin_headers, b"timestamp,username\n2026-10-24T08:00:00Z,alice\n")
    assert r.status_code == 422
    assert "Colonnes manquantes" in r.json()["detail"]


def test_non_csv_extension_rejected(client, admin_headers):
    assert upload(client, admin_headers, b"x", name="logs.exe").status_code == 400


def test_analyst_cannot_import(client, analyst_headers):
    assert upload(client, analyst_headers, SAMPLE.read_bytes()).status_code == 403


def test_import_requires_login(client):
    r = client.post("/events/import", files={"file": ("a.csv", b"x", "text/csv")})
    assert r.status_code == 401


def test_list_pagination_and_filters(client, admin_headers, analyst_headers):
    upload(client, admin_headers, SAMPLE.read_bytes())
    r = client.get("/events?page_size=10", headers=analyst_headers)  # un analyste peut lire
    body = r.json()
    assert body["total"] == 219 and len(body["items"]) == 10

    r = client.get("/events?source_ip=192.0.2.99", headers=analyst_headers)
    assert r.json()["total"] == 8

    r = client.get("/events?username=bob&status=failure", headers=analyst_headers)
    assert r.json()["total"] >= 8


def test_list_requires_login(client):
    assert client.get("/events").status_code == 401