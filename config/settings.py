"""
Configuration centralisee du projet Talk2CVs
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

# Configuration Embeddings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Configuration Review & Email
TOP_CANDIDATES = int(os.getenv("TOP_CANDIDATES", "5"))
EMAIL_SUBJECT = "Mise a jour de votre candidature"
EMAIL_BODY = """Bonjour,

Suite a l'examen de votre candidature, nous avons le plaisir de vous informer que votre profil a ete retenu pour la prochaine etape du recrutement

Cordialement,"""

print(f"Configuration chargee")
print(f"   - Modele Ollama : {OLLAMA_MODEL}")
print(f"   - Modele Embeddings : {EMBEDDING_MODEL}")
