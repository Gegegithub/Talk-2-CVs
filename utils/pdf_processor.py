"""
Traitement et ingestion des CVs au format PDF
Adapté de ingest.py - VERSION SANS IMAGES (texte uniquement)
"""
from pathlib import Path
from typing import List
from tqdm import tqdm

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from utils.vector_store import get_vector_store


class PDFProcessor:
    """Processeur de CVs PDF pour ingestion dans ChromaDB"""

    def __init__(self):
        """Initialise le text splitter"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],  # Ordre de priorité
            length_function=len,
        )
        self.vector_store = get_vector_store()

    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """
        Charge et découpe un PDF en chunks

        Args:
            pdf_path: Chemin vers le fichier PDF

        Returns:
            Liste de Documents LangChain avec métadonnées
        """
        try:
            # Charger le PDF
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()

            # Découper en chunks
            chunks = self.text_splitter.split_documents(pages)

            # Ajouter des métadonnées personnalisées
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "source": pdf_path.name,  # Nom du fichier uniquement
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_type": "pdf"
                })

            return chunks

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {pdf_path.name}: {e}")
            return []

    def ingest_all_pdfs(self, reset_db: bool = False) -> int:
        """
        Ingère tous les PDFs du dossier data/

        Args:
            reset_db: Si True, vide la base avant ingestion

        Returns:
            Nombre total de chunks ingérés
        """
        # Optionnel : Réinitialiser la base
        if reset_db:
            print("⚠️  Réinitialisation de la base vectorielle...")
            self.vector_store.reset()

        # Trouver tous les PDFs
        pdf_files = list(DATA_DIR.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠️  Aucun fichier PDF trouvé dans {DATA_DIR}")
            return 0

        print(f"\n📂 Trouvé {len(pdf_files)} fichier(s) PDF à ingérer\n")

        all_chunks = []

        # Traiter chaque PDF
        for pdf_path in tqdm(pdf_files, desc="Traitement des CVs"):
            chunks = self.process_pdf(pdf_path)
            all_chunks.extend(chunks)
            print(f"   ✅ {pdf_path.name}: {len(chunks)} chunks")

        # Ingestion dans ChromaDB via LangChain
        if all_chunks:
            print(f"\n💾 Ingestion de {len(all_chunks)} chunks dans ChromaDB...")
            vectorstore = self.vector_store.get_vectorstore()
            vectorstore.add_documents(all_chunks)
            print(f"✅ Ingestion terminée !\n")

        # Afficher les stats
        stats = self.vector_store.get_stats()
        print(f"📊 Statistiques finales:")
        print(f"   - Collection: {stats['collection_name']}")
        print(f"   - Total chunks: {stats['total_chunks']}")
        print(f"   - Statut: {stats['status']}")

        return len(all_chunks)


def ingest_pdfs(reset_db: bool = False) -> int:
    """
    Fonction helper pour ingérer les PDFs

    Args:
        reset_db: Si True, vide la base avant ingestion

    Returns:
        Nombre de chunks ingérés
    """
    processor = PDFProcessor()
    return processor.ingest_all_pdfs(reset_db=reset_db)
