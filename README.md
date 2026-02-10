# Talk2cvs

##  Aperçu
<img width="1388" height="533" alt="Image" src="https://github.com/user-attachments/assets/f54b3ec4-7e2e-4279-bcc0-377397169db1" />

**Système RAG 100% local pour analyser des CVs en langage naturel**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3.1-orange)


---

##  Problématique

Les recruteurs perdent du temps à lire manuellement des dizaines de CVs. Cette application permet de poser des questions en langage naturel :

> "Qui maîtrise Python, SQL et Kafka ?"

→ Le système retourne **uniquement** les candidats correspondant à **tous** les critères, avec preuves extraites des CVs.

---

##  Fonctionnalités

-  **100% Local** - Aucune donnée envoyée vers le cloud
-  **Upload direct** - Glissez vos CVs via l'interface chat
-  **Conversation naturelle** - Mémoire des échanges précédents
-  **Statistiques** - Suivi des CVs indexés en temps réel
-  **Interface moderne** - Style inspiré de Gemini

---

##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Upload PDF  │  │ Chat Input  │  │ Suggestions     │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  LangChain RAG Pipeline                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ PDF Parser  │  │ Embeddings  │  │ Chat History    │  │
│  │ (pypdf)     │  │ (MiniLM)    │  │ (6 derniers)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  ChromaDB          │           Ollama                   │
│  (Vector Store)    │        (Llama 3.1 8B)              │
│  Top-15 chunks     │      Génération réponse            │
└────────────────────┴────────────────────────────────────┘
```

---

##  Installation

### Prérequis

- Python 3.10+
- [Ollama](https://ollama.com/download) installé
- 8GB RAM minimum (16GB recommandé)

### Étapes

```bash
# 1. Cloner le repository
git clone 
cd talk2cvs

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env

# 5. Télécharger un modèle Ollama
ollama pull llama3.1:8b   # Recommandé

# 6. Lancer l'application
streamlit run app.py
```

→ Ouvrir http://localhost:8501

---
##  Structure du Projet

```
talk2cvs/
├── data/                    # CVs en PDF (uploadés via l'app)
├── chroma_db/               # Base vectorielle (auto-généré)
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration centralisée
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py     # Parsing et chunking PDFs
│   └── vector_store.py      # Gestion ChromaDB
├── agents/
│   ├── __init__.py
│   └── recruiter_rag.py     # Pipeline RAG avec LCEL
├── app.py                   # Interface Streamlit
├── explore_db.py            # Script pour explorer ChromaDB
├── run_ingestion.py         # Script d'ingestion CLI (optionnel)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Ollama (Llama 3.1 8B) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persistant) |
| Framework | LangChain + LCEL |
| Frontend | Streamlit 1.41+ |
| PDF Parsing | pypdf |

---
