# -*- coding: utf-8 -*-
"""
Utilitaires pour l'extraction d'informations depuis les CVs
- Email (regex)
- Nom du candidat (depuis le nom de fichier)
"""
import re


def extract_email(text: str) -> str:
    """
    Extrait le premier email trouve dans le texte d'un CV.

    Args:
        text: Texte brut extrait du PDF

    Returns:
        Email trouve ou chaine vide
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


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
    name = re.sub(r'\s*\(\d+\)\s*', ' ', name)
    # Nettoyer
    name = name.replace("-", " ").replace("_", " ")
    name = " ".join(name.split())
    return name.title()
