from fastapi import FastAPI
# crée notre API.
app = FastAPI(
    title = "SentinelLLite API",
    description = "application de detection d'activités suspects",
    version = "0.1.0"
)
# affiche un message d’accueil.
@app.get("/")
def acceuil():
    return {
        "projet": "SentinelLLite",
        "message": "Bienvenue sur l'API de SentinelLLite"       
    }
#permet de vérifier que le service fonctionne.
@app.get("/health")
def health():
    return {
        "status": "ok",
    }