"""
Script d'ingestion des CVs dans ChromaDB
Lance ce script pour indexer tous les PDFs du dossier data/
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from utils.pdf_processor import ingest_pdfs
from config.settings import DATA_DIR


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🚀 LOCAL RECRUITER ASSISTANT - INGESTION DE CVs")
    print("=" * 60)
    print()

    # Vérifier que le dossier data/ contient des PDFs
    pdf_count = len(list(DATA_DIR.glob("*.pdf")))

    if pdf_count == 0:
        print(f"⚠️  ATTENTION : Aucun fichier PDF trouvé dans {DATA_DIR}")
        print()
        print("👉 Pour continuer :")
        print(f"   1. Placez vos CVs (fichiers .pdf) dans le dossier : {DATA_DIR}")
        print("   2. Relancez ce script")
        print()
        return

    # Demander confirmation pour reset
    print(f"📂 {pdf_count} fichier(s) PDF détecté(s)")
    print()
    reset = input("Voulez-vous réinitialiser la base avant ingestion ? (o/N) : ").strip().lower()
    reset_db = reset == 'o'

    print()

    # Lancer l'ingestion
    total_chunks = ingest_pdfs(reset_db=reset_db)

    print()
    print("=" * 60)
    if total_chunks > 0:
        print("✅ INGESTION TERMINÉE AVEC SUCCÈS")
        print(f"   → {total_chunks} chunks indexés")
        print()
        print("👉 Vous pouvez maintenant lancer l'application :")
        print("   streamlit run app.py")
    else:
        print("❌ AUCUN CHUNK N'A ÉTÉ INDEXÉ")
        print("   Vérifiez que vos PDFs contiennent du texte extractible")
    print("=" * 60)


if __name__ == "__main__":
    main()
