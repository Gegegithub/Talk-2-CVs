# RAG Multimodal

Systeme de Retrieval-Augmented Generation (RAG) avec support multimodal permettant d'indexer et d'interroger des documents PDF et des images.

## Description

Ce projet implémente un pipeline RAG complet qui :

- Extrait le texte des fichiers PDF
- Génère des descriptions automatiques des images via Gemini
- Stocke les embeddings dans une base de données vectorielle (PostgreSQL + pgvector)
- Permet de poser des questions en langage naturel via une interface web

## Architecture

```
Documents (PDFs, Images)
        |
        v
+------------------+
|    Ingestion     |  <- ingest.py
|  - Extraction    |
|  - Chunking      |
|  - Captioning    |
+------------------+
        |
        v
+------------------+
|    Embeddings    |  <- gemini_utils.py
| text-embedding-  |
|      004         |
+------------------+
        |
        v
+------------------+
|   PostgreSQL     |  <- db.py
|   + pgvector     |
+------------------+
        |
        v
+------------------+
|   Retrieval &    |  <- rag_core.py
|   Generation     |
|  (Gemini Flash)  |
+------------------+
        |
        v
+------------------+
|   Interface      |  <- app.py
|   Streamlit      |
+------------------+
```

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- Clé API Google (Gemini)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/rag-multimodal.git
cd rag-multimodal
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
GOOGLE_API_KEY=votre-cle-api-gemini
PG_HOST=localhost
PG_PORT=5433
PG_DB=ragdb
PG_USER=raguser
PG_PASSWORD=ragpass
```

Pour obtenir une clé API Gemini : [Google AI Studio](https://aistudio.google.com/apikey)

### 5. Lancer la base de données

```bash
docker-compose up -d
```

### 6. Créer la table des documents

```bash
docker exec -it pgvector_rag psql -U raguser -d ragdb -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE TABLE documents (id SERIAL PRIMARY KEY, source TEXT, chunk TEXT, modality TEXT, embedding vector(768));"
```

## Utilisation

### Ingestion des documents

Placer vos fichiers PDF et images (PNG, JPG) dans le dossier `data/`, puis exécuter :

```bash
python ingest.py
```

Le script va :
- Extraire le texte des PDFs et le découper en chunks de 800 caractères
- Générer des descriptions pour chaque image via Gemini Flash
- Créer les embeddings et les stocker dans la base de données

### Lancer l'interface web

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## Structure du projet

```
rag-multimodal/
├── app.py              # Interface Streamlit
├── rag_core.py         # Logique RAG (retrieval + generation)
├── ingest.py           # Pipeline d'ingestion des documents
├── db.py               # Connexion PostgreSQL
├── gemini_utils.py     # Utilitaires Gemini (embeddings, captioning)
├── docker-compose.yml  # Configuration PostgreSQL + pgvector
├── requirements.txt    # Dépendances Python
├── data/               # Dossier des documents à indexer
└── .env                # Variables d'environnement (non versionné)
```

## Description des fichiers

### app.py

Point d'entrée de l'application. Ce fichier crée l'interface web avec Streamlit :
- Affiche un champ de saisie pour poser des questions
- Appelle le module `rag_core` pour obtenir les réponses
- Affiche la réponse générée par le LLM à gauche
- Montre les sources et scores de similarité à droite

### rag_core.py

Coeur du système RAG contenant deux fonctions principales :
- `retrieve(query, k)` : Convertit la question en embedding, effectue une recherche par similarité cosinus dans PostgreSQL et retourne les k chunks les plus pertinents
- `answer(query, k)` : Orchestre le pipeline complet en appelant `retrieve()`, construisant le contexte à partir des chunks, puis envoyant le tout à Gemini pour générer une réponse

### ingest.py

Pipeline d'ingestion des documents avec les fonctions :
- `chunk_text(text, size, overlap)` : Découpe le texte en morceaux de taille fixe avec chevauchement pour préserver le contexte
- `ingest_pdf(path)` : Extrait le texte de chaque page d'un PDF via pypdf, le découpe en chunks et les stocke
- `ingest_images(path)` : Envoie l'image à Gemini Flash pour obtenir une description textuelle, puis stocke cette description
- `save_chunk(source, chunk, modality)` : Génère l'embedding du chunk et l'insère dans la base de données
- `main()` : Parcourt le dossier `data/` et traite tous les fichiers PDF et images

### db.py

Module de connexion à la base de données :
- `get_conn()` : Crée une connexion PostgreSQL en utilisant les variables d'environnement et enregistre l'extension pgvector pour manipuler les vecteurs

### gemini_utils.py

Utilitaires pour interagir avec l'API Gemini :
- `embed_text(text)` : Convertit un texte en vecteur de 768 dimensions via le modèle text-embedding-004
- `caption_image(path)` : Envoie l'image à Gemini Flash et retourne une description textuelle de 2-3 phrases optimisée pour la recherche

### docker-compose.yml

Configuration Docker pour lancer PostgreSQL avec l'extension pgvector :
- Utilise l'image `pgvector/pgvector:pg16`
- Expose le port 5433 pour éviter les conflits avec une installation PostgreSQL locale
- Configure un volume persistant pour les données

### requirements.txt

Liste des dépendances Python nécessaires :
- `google-generativeai` : Client API Gemini
- `psycopg2-binary` : Driver PostgreSQL
- `pgvector` : Support des vecteurs dans Python
- `pypdf` : Extraction de texte des PDFs
- `pillow` : Manipulation d'images
- `python-dotenv` : Chargement des variables d'environnement
- `tqdm` : Barres de progression
- `streamlit` : Framework d'interface web

## Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Base vectorielle | PostgreSQL 16 + pgvector |
| Embeddings | Gemini text-embedding-004 (768 dim) |
| Vision | Gemini Flash |
| LLM | Gemini Flash |
| Extraction PDF | pypdf |
| Traitement images | Pillow |

## Fonctionnement

### Ingestion

1. Les PDFs sont parsés et le texte est extrait page par page
2. Le texte est découpé en chunks de 800 caractères avec un chevauchement de 100 caractères
3. Les images sont envoyées à Gemini Flash pour générer une description textuelle
4. Chaque chunk (texte ou description d'image) est converti en vecteur via l'API Gemini
5. Les vecteurs sont stockés dans PostgreSQL avec leur source et modalité

### Requête

1. La question de l'utilisateur est convertie en vecteur
2. Une recherche par similarité cosinus récupère les 5 chunks les plus pertinents
3. Les chunks sont assemblés en contexte
4. Le contexte et la question sont envoyés à Gemini Flash
5. La réponse est affichée avec les sources utilisées

## Limites du plan gratuit Gemini

Le plan gratuit de l'API Gemini a des limites :
- 15 requêtes/minute
- 1500 requêtes/jour

Pour une utilisation intensive, activez la facturation sur votre projet Google Cloud.
