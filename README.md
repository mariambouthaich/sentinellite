# SentinelLite

Mini-SIEM : import de logs synthétiques, détection d'activités suspectes par règles, et tableau de bord d'alertes.

## Technologies

FastAPI • PostgreSQL • SQLAlchemy • Docker • (React et Scikit-learn à venir)

## Démarrage rapide

```bash
# 1. Configuration
cp .env.example .env          # puis modifie le mot de passe

# 2. Base de données
docker compose up -d db

# 3. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API : http://127.0.0.1:8000 • Documentation : http://127.0.0.1:8000/docs

## Données de démonstration

```bash
python scripts/generate_sample_logs.py
```

Génère `data/sample_logs.csv` (événements normaux + scénarios d'attaque simulés).

## État du projet

- [x] Dépôt, Docker Compose, logs synthétiques
- [ ] Modèles et migrations
- [ ] Authentification
- [ ] Import et règles de détection
- [ ] Dashboard
