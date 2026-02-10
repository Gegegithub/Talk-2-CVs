# -*- coding: utf-8 -*-
"""
Script pour explorer le contenu de ChromaDB
"""
import chromadb
from chromadb.config import Settings

# Connexion
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

# Lister les collections
print("=" * 50)
print("COLLECTIONS DISPONIBLES")
print("=" * 50)
collections = client.list_collections()
for col in collections:
    print(f"  - {col.name}")

# Acceder a la collection des CVs
try:
    collection = client.get_collection("cv_collection")
    count = collection.count()

    print(f"\n{'=' * 50}")
    print(f"COLLECTION: cv_collection")
    print(f"{'=' * 50}")
    print(f"Nombre de chunks: {count}")

    if count > 0:
        # Recuperer les documents
        results = collection.get(
            limit=20,
            include=["documents", "metadatas"]
        )

        print(f"\n{'=' * 50}")
        print("DOCUMENTS (20 premiers)")
        print("=" * 50)

        # Grouper par source
        sources = {}
        for i, doc_id in enumerate(results["ids"]):
            source = results["metadatas"][i].get("source", "Inconnu")
            if source not in sources:
                sources[source] = []
            sources[source].append({
                "id": doc_id,
                "chunk_id": results["metadatas"][i].get("chunk_id", 0),
                "content": results["documents"][i][:150] + "..."
            })

        for source, chunks in sources.items():
            print(f"\n[FILE] {source} ({len(chunks)} chunks)")
            print("-" * 40)
            for chunk in chunks[:3]:
                print(f"  [Chunk {chunk['chunk_id']}] {chunk['content'][:100]}...")
            if len(chunks) > 3:
                print(f"  ... et {len(chunks) - 3} autres chunks")
    else:
        print("\n[!] La base est vide. Upload des CVs via Streamlit.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("La collection n'existe peut-etre pas encore.")

print(f"\n{'=' * 50}")
