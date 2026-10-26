import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)
START = datetime(2026, 10, 24, 8, 0, tzinfo=timezone.utc)
USERS = ["mariam", "oussama", "asmaa", "manal", "morad"]
HOME_IP = {u: f"192.0.2.{10 + i}" for i, u in enumerate(USERS)}
rows = []

def add(ts, ip, user, etype, status, source="synthetic-auth-log"):
    rows.append({"timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "source_ip": ip,
                 "username": user, "event_type": etype, "status": status, "source": source})

# 1) Trafic normal
for _ in range(200):
    u = random.choice(USERS)
    ts = START + timedelta(minutes=random.randint(0, 600), seconds=random.randint(0, 59))
    if random.random() < 0.05:
        add(ts, HOME_IP[u], u, "login_failed", "failure")
    else:
        add(ts, HOME_IP[u], u, "login_success", "success")

# 2) R1 : 8 échecs sur "bob" en 3 minutes
t = START + timedelta(hours=3)
for i in range(8):
    add(t + timedelta(seconds=i * 22), "192.0.2.99", "bob", "login_failed", "failure")

# 3) R2 : une IP teste plusieurs comptes
t = START + timedelta(hours=5)
for i, u in enumerate(USERS * 2):
    add(t + timedelta(seconds=i * 15), "192.0.2.150", u, "login_failed", "failure")

# 4) R4 : connexion de nuit
add(datetime(2026, 10, 25, 3, 12, tzinfo=timezone.utc), "192.0.2.77", "carol", "login_success", "success")

rows.sort(key=lambda r: r["timestamp"])
out = Path(__file__).resolve().parent.parent / "data" / "sample_logs.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["timestamp", "source_ip", "username", "event_type", "status", "source"])
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} événements écrits dans {out}")