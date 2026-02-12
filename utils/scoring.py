# -*- coding: utf-8 -*-
"""
Scoring des CVs par rapport a une description de poste
Utilise la similarite cosinus entre embeddings
Embede uniquement les sections pertinentes (competences, projets, experiences)
"""
import re
from typing import List, Dict
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL


# Singleton pour le modele d'embeddings
_embeddings_instance = None


def get_embeddings():
    """Recupere l'instance singleton du modele d'embeddings"""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings_instance


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcule la similarite cosinus entre deux vecteurs"""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def extract_relevant_sections(text: str) -> str:
    """
    Extrait les sections pertinentes d'un CV (competences, projets, experiences).
    Si aucune section n'est trouvee, retourne le texte entier.
    """
    # Mots-cles de sections pertinentes (FR + EN)
    section_keywords = [
        r"comp[ée]tences?",
        r"skills?",
        r"technologies?",
        r"outils?",
        r"tools?",
        r"projets?",
        r"projects?",
        r"exp[ée]riences?",
        r"experiences?",
        r"r[ée]alisations?",
        r"stack\s*technique",
        r"technical\s*skills?",
        r"langages?",
        r"frameworks?",
    ]

    # Pattern pour detecter un titre de section
    section_pattern = re.compile(
        r"^[\s•\-]*(" + "|".join(section_keywords) + r")[\s:]*$",
        re.IGNORECASE | re.MULTILINE
    )

    # Pattern pour detecter n'importe quel titre de section (pour delimiter la fin)
    any_section_pattern = re.compile(
        r"^[\s•\-]*[A-ZÀ-Ü][a-zà-ü]+(?:\s+[a-zà-ü&]+)*[\s:]*$",
        re.MULTILINE
    )

    lines = text.split("\n")
    relevant_parts = []
    capturing = False
    current_section = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if capturing:
                current_section.append("")
            continue

        # Est-ce un titre de section pertinente ?
        if section_pattern.match(stripped):
            if current_section:
                relevant_parts.extend(current_section)
            current_section = [stripped]
            capturing = True
        # Est-ce un autre titre de section (fin de la section pertinente) ?
        elif capturing and any_section_pattern.match(stripped) and not section_pattern.match(stripped):
            if current_section:
                relevant_parts.extend(current_section)
                current_section = []
            capturing = False
        elif capturing:
            current_section.append(stripped)

    # Ajouter la derniere section capturee
    if current_section:
        relevant_parts.extend(current_section)

    result = "\n".join(relevant_parts).strip()

    # Si rien de pertinent trouve, retourner le texte entier
    if not result or len(result) < 50:
        return text

    return result


def score_candidates(
    job_description: str,
    candidates: List[Dict],
    top_n: int = 5
) -> List[Dict]:
    """
    Score chaque candidat par rapport a la description de poste.

    Args:
        job_description: Texte de la description de poste
        candidates: Liste de dicts avec 'name', 'email', 'text', 'filename'
        top_n: Nombre de candidats a retenir

    Returns:
        Liste des top_n candidats tries par score decroissant
    """
    embeddings = get_embeddings()

    # Embedding de la description de poste
    jd_embedding = embeddings.embed_query(job_description)

    # Scorer chaque candidat sur les sections pertinentes
    for candidate in candidates:
        relevant_text = extract_relevant_sections(candidate["text"])
        cv_embedding = embeddings.embed_query(relevant_text)
        candidate["score"] = cosine_similarity(jd_embedding, cv_embedding)

    # Trier par score decroissant et garder les top_n
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]
