"""
Gestion de ChromaDB pour le stockage et la recherche vectorielle
"""
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import CHROMA_DIR, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL


class VectorStoreManager:
    """Gestionnaire de la base de données vectorielle ChromaDB"""

    def __init__(self):
        """Initialise ChromaDB et les embeddings"""
        print("🔧 Initialisation du Vector Store...")

        # Initialiser les embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},  # Utilise GPU si disponible
            encode_kwargs={'normalize_embeddings': True}
        )

        # Initialiser ChromaDB (client persistant)
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialiser le vector store LangChain
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=str(CHROMA_DIR)
        )

        print(f"✅ Vector Store initialisé ({CHROMA_COLLECTION_NAME})")

    def get_vectorstore(self):
        """Retourne l'instance du vector store"""
        return self.vectorstore

    def get_stats(self) -> Dict:
        """Retourne les statistiques de la base vectorielle"""
        try:
            collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            count = collection.count()
            return {
                "collection_name": CHROMA_COLLECTION_NAME,
                "total_chunks": count,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            return {
                "collection_name": CHROMA_COLLECTION_NAME,
                "total_chunks": 0,
                "status": "error",
                "error": str(e)
            }

    def get_all_documents(self, limit: int = 100) -> List[Dict]:
        """
        Récupère tous les documents de la collection

        Args:
            limit: Nombre maximum de documents à retourner

        Returns:
            Liste de dictionnaires avec 'id', 'content', 'metadata'
        """
        try:
            collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            results = collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )

            documents = []
            for i, doc_id in enumerate(results["ids"]):
                documents.append({
                    "id": doc_id,
                    "content": results["documents"][i] if results["documents"] else "",
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })

            return documents
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des documents : {e}")
            return []

    def get_unique_sources(self) -> List[str]:
        """Retourne la liste des fichiers sources uniques"""
        documents = self.get_all_documents(limit=1000)
        sources = set()
        for doc in documents:
            source = doc.get("metadata", {}).get("source", "")
            if source:
                sources.add(source)
        return sorted(list(sources))

    def reset(self):
        """Réinitialise complètement la base vectorielle (ATTENTION: supprime tout)"""
        try:
            self.client.delete_collection(CHROMA_COLLECTION_NAME)
            print(f"⚠️  Collection '{CHROMA_COLLECTION_NAME}' supprimée")

            # Recréer le vector store
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=CHROMA_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(CHROMA_DIR)
            )
            print(f"✅ Nouvelle collection créée")
        except Exception as e:
            print(f"❌ Erreur lors du reset : {e}")


# Instance globale (singleton)
_vector_store_instance = None


def get_vector_store() -> VectorStoreManager:
    """Récupère l'instance singleton du VectorStoreManager"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreManager()
    return _vector_store_instance
