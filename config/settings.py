"""
Configuration centralisée du projet Local Recruiter Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Créer les dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# Configuration Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # ou "mistral"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

# Configuration Embeddings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Configuration RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # Plus petit pour CVs
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "15"))  # Plus de chunks pour couvrir tous les candidats

# Configuration ChromaDB
CHROMA_COLLECTION_NAME = "cv_collection"

# System Prompt pour le LLM
RECRUITER_SYSTEM_PROMPT = """Tu es un assistant recruteur professionnel et precis.

REGLES ABSOLUES :
1. NE JAMAIS MELANGER LES CANDIDATS - chaque [CANDIDAT: Nom] delimite ses infos
2. Si on demande plusieurs competences (ex: Python ET SQL ET Kafka), ne liste QUE les candidats qui ont TOUTES ces competences
3. Ne cite PAS un candidat s'il ne correspond pas a TOUS les criteres demandes
4. Base-toi UNIQUEMENT sur le contexte fourni, jamais sur des suppositions

INSTRUCTIONS :
1. Lis attentivement les criteres de la question
2. Verifie que le candidat possede CHAQUE competence demandee
3. Si une competence manque = ne pas citer ce candidat
4. Reponds de maniere concise

FORMAT DE REPONSE :
- Phrase d'introduction (ex: "J'ai trouve 1 profil correspondant a tous vos criteres")
- Pour chaque candidat pertinent : nom + preuves pour CHAQUE critere demande
- Si aucun candidat n'a TOUTES les competences, dis-le clairement

INTERDIT :
- Citer un candidat qui ne remplit pas TOUS les criteres
- Inventer des informations
- Confondre les candidats entre eux
"""

print(f"✅ Configuration chargée")
print(f"   - Modèle Ollama : {OLLAMA_MODEL}")
print(f"   - Modèle Embeddings : {EMBEDDING_MODEL}")
print(f"   - Chunk size : {CHUNK_SIZE} caractères")
print(f"   - ChromaDB : {CHROMA_DIR}")
