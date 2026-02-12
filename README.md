# Talk2CVs

## Apercu


**Application 100% locale pour analyser et trier des CVs par rapport a une description de poste**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3.1-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red)

---

## Problematique

Les recruteurs perdent du temps a lire manuellement des dizaines de CVs. Cette application automatise le tri :

1. Upload des CVs + description du poste
2. Le scoring par embeddings classe les candidats par pertinence
3. Le LLM explique pourquoi chaque candidat correspond (ou pas)
4. Navigation dans les CVs et contact des candidats en un clic

---

## Fonctionnalites

- **100% Local** - Aucune donnee envoyee vers le cloud
- **Scoring intelligent** - Embeddings sur les sections pertinentes (competences, projets, experiences)
- **Analyse LLM** - Explication detaillee pour chaque candidat retenu
- **Apercu PDF** - Consultation des CVs directement dans l'interface
- **Contact groupe** - Lien mailto avec tous les candidats retenus en BCC

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  Mode Analyse    │  │  Mode CVs & Contact          │ │
│  │  Upload + Score  │  │  Carrousel PDF + Mailto      │ │
│  └──────────────────┘  └──────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│              Scoring + Analyse                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ PDF Parser  │  │ Embeddings  │  │ LLM             │ │
│  │ (pypdf)     │  │ (MiniLM)    │  │ (Ollama)        │ │
│  │ Extraction  │  │ Similarite  │  │ Recommandations │ │
│  │ texte+email │  │ cosinus     │  │ detaillees      │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequis

- Python 3.10+
- [Ollama](https://ollama.com/download) installe
- 8GB RAM minimum (16GB recommande)

### Etapes

```bash
# 1. Cloner le repository
git clone
cd talk2cvs

# 2. Creer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env

# 5. Telecharger un modele Ollama
ollama pull llama3.1:8b

# 6. Lancer l'application
streamlit run app.py
```

Ouvrir http://localhost:8501

---

## Structure du Projet

```
talk2cvs/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration (Ollama, Embeddings, Email)
├── utils/
│   ├── __init__.py
│   ├── email_extractor.py   # Extraction email + nom depuis les CVs
│   └── scoring.py           # Scoring par embeddings + similarite cosinus
├── app.py                   # Interface Streamlit (Analyse + CVs & Contact)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Ollama (Llama 3.1 8B) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Scoring | Similarite cosinus entre embeddings |
| Frontend | Streamlit 1.41+ |
| PDF Parsing | pypdf |

---
