# -*- coding: utf-8 -*-
"""
Agent RAG pour le recrutement
Version LOCALE avec Ollama + LangChain (LCEL)
"""
from typing import Dict, List
from langchain_community.llms import Ollama  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from langchain_core.documents import Document  # type: ignore
from langchain_core.output_parsers import StrOutputParser  # type: ignore
from langchain_core.runnables import RunnablePassthrough  # type: ignore

from config.settings import (
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_TEMPERATURE,
    TOP_K_RESULTS,
    RECRUITER_SYSTEM_PROMPT
)
from utils.vector_store import get_vector_store


import re


def extract_name_from_filename(filename: str) -> str:
    """Extrait un nom propre depuis le nom de fichier PDF"""
    name = filename
    # Retirer toutes les extensions .pdf (meme multiples)
    while name.lower().endswith(".pdf"):
        name = name[:-4]
    # Retirer les prefixes courants
    for prefix in ["CV-", "CV_", "cv-", "cv_", "CV ", "Resume-", "resume-"]:
        name = name.replace(prefix, "")
    # Retirer les numeros de version (1), (2), etc.
    import re
    name = re.sub(r'\s*\(\d+\)\s*', ' ', name)
    # Nettoyer
    name = name.replace("-", " ").replace("_", " ")
    name = " ".join(name.split())
    return name.title()


def extract_name_from_content(content: str) -> str:
    """Essaie d'extraire le nom depuis le contenu du CV"""
    # Prendre les 500 premiers caracteres (le nom est souvent au debut)
    header = content[:500]

    # Pattern: 2-3 mots commencant par majuscule en debut de ligne
    patterns = [
        r'^([A-Z][a-zéèêëàâäùûüôöîï]+\s+[A-Z][A-Zéèêëàâäùûüôöîï]+(?:\s+[A-Z][a-zéèêëàâäùûüôöîï]+)?)',
        r'([A-Z][A-Z]+\s+[A-Z][a-zéèêëàâäùûüôöîï]+)',  # NOM Prenom
        r'([A-Z][a-zéèêëàâäùûüôöîï]+\s+[A-Z][A-Z]+)',  # Prenom NOM
    ]

    for pattern in patterns:
        match = re.search(pattern, header, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            # Verifier que ca ressemble a un nom (2-4 mots, pas trop long)
            words = name.split()
            if 2 <= len(words) <= 4 and len(name) < 40:
                return name.title()

    return ""


def get_candidate_name(filename: str, content: str) -> str:
    """Determine le nom du candidat (fichier ou contenu)"""
    # D'abord essayer depuis le nom de fichier
    name_from_file = extract_name_from_filename(filename)

    # Si le nom de fichier semble generique, chercher dans le contenu
    generic_names = ["document", "cv", "resume", "fichier", "scan", "pdf"]
    if name_from_file.lower() in generic_names or len(name_from_file) < 3:
        name_from_content = extract_name_from_content(content)
        if name_from_content:
            return name_from_content

    return name_from_file if name_from_file else "Candidat Inconnu"


def format_docs(docs: List[Document]) -> str:
    """Formate les documents pour le contexte avec le nom du candidat"""
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "Inconnu")
        content = doc.page_content
        candidate_name = get_candidate_name(source, content)
        # Formatage tres clair pour eviter la confusion
        formatted.append(
            f"========== DEBUT CV: {candidate_name} ==========\n"
            f"{content}\n"
            f"========== FIN CV: {candidate_name} =========="
        )
    return "\n\n".join(formatted)


class RecruiterRAG:
    """Agent RAG specialise pour le recrutement"""

    def __init__(self):
        """Initialise le LLM et le pipeline RAG"""
        print("Initialisation de l'agent RAG...")

        # Initialiser Ollama
        self.llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=OLLAMA_TEMPERATURE,
        )

        # Recuperer le vector store
        vector_store_manager = get_vector_store()
        self.vectorstore = vector_store_manager.get_vectorstore()

        # Configurer le retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K_RESULTS}
        )

        # Creer le prompt template avec historique
        self.prompt = ChatPromptTemplate.from_template(
            f"""{RECRUITER_SYSTEM_PROMPT}

HISTORIQUE DE LA CONVERSATION :
{{chat_history}}

CONTEXTE (extraits des CVs) :
{{context}}

QUESTION DU RECRUTEUR :
{{question}}

REPONSE (sois concis si c'est une question de suivi) :"""
        )

        print(f"Agent RAG initialise (modele: {OLLAMA_MODEL})")

    def query(self, question: str, chat_history: List[Dict] = None) -> Dict:
        """
        Interroge la base de CVs

        Args:
            question: Question du recruteur
            chat_history: Historique de la conversation (optionnel)

        Returns:
            Dict avec 'answer', 'sources', et 'source_documents'
        """
        try:
            # Formater l'historique
            history_str = ""
            if chat_history:
                for msg in chat_history[-6:]:  # Garder les 6 derniers messages
                    role = "Recruteur" if msg["role"] == "user" else "Assistant"
                    history_str += f"{role}: {msg['content'][:300]}\n"

            # Recuperer les documents sources
            source_docs = self.retriever.invoke(question)

            # Construire la chaine manuellement pour inclure l'historique
            context = format_docs(source_docs)
            prompt_value = self.prompt.invoke({
                "context": context,
                "question": question,
                "chat_history": history_str if history_str else "(Nouvelle conversation)"
            })

            # Executer le LLM
            answer = self.llm.invoke(prompt_value)

            # Extraire les sources
            sources = self._extract_sources(source_docs)

            return {
                "answer": answer,
                "sources": sources,
                "source_documents": source_docs
            }

        except Exception as e:
            return {
                "answer": f"Erreur lors de la requete : {str(e)}",
                "sources": [],
                "source_documents": []
            }

    def _extract_sources(self, documents: List[Document]) -> List[Dict]:
        """Extrait les informations des sources"""
        sources = []
        seen_sources = set()

        for doc in documents:
            source_name = doc.metadata.get("source", "Inconnu")

            # Eviter les doublons
            if source_name not in seen_sources:
                sources.append({
                    "file": source_name,
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "preview": doc.page_content[:200] + "..."
                })
                seen_sources.add(source_name)

        return sources

    def get_retriever_stats(self) -> Dict:
        """Retourne les statistiques du retriever"""
        vector_store_manager = get_vector_store()
        return vector_store_manager.get_stats()


# Instance globale
_rag_instance = None


def get_rag_agent() -> RecruiterRAG:
    """Recupere l'instance singleton du RAG"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RecruiterRAG()
    return _rag_instance


def answer(question: str, chat_history: List[Dict] = None) -> Dict:
    """
    Helper function pour compatibilite avec app.py

    Args:
        question: Question du recruteur
        chat_history: Historique de la conversation

    Returns:
        Resultat de la requete RAG
    """
    rag = get_rag_agent()
    return rag.query(question, chat_history)
