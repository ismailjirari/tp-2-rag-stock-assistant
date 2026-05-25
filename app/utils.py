# utils.py

import re
import json
import os
from config import CHUNK_SIZE, CHUNK_OVERLAP, PROCESSED_DATA_PATH


def clean_text(text: str) -> str:
    """Nettoie le texte brut extrait du PDF en préservant la structure."""
    # Normaliser les sauts de ligne multiples (garder max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Supprimer les espaces multiples sur une même ligne
    text = re.sub(r'[ \t]+', ' ', text)
    # Supprimer les caractères vraiment inutiles (garder accents, ponctuation)
    text = re.sub(r'[^\w\s\.,;:!?()\-–/\'\"àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ\n]', '', text)
    text = text.strip()
    return text


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Découpe le texte en chunks avec chevauchement (basé sur les mots)."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def save_chunks(chunks: list[dict], filename: str = "chunks.json"):
    """Sauvegarde les chunks dans le dossier processed."""
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    filepath = os.path.join(PROCESSED_DATA_PATH, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(chunks)} chunks sauvegardés dans {filepath}")


def load_chunks(filename: str = "chunks.json") -> list[dict]:
    """Charge les chunks depuis le dossier processed."""
    filepath = os.path.join(PROCESSED_DATA_PATH, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier non trouvé : {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"✅ {len(chunks)} chunks chargés depuis {filepath}")
    return chunks


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrait le texte d'un fichier PDF page par page."""
    try:
        import pypdf
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)

            if reader.is_encrypted:
                reader.decrypt("")

            total_pages = len(reader.pages)
            print(f"   → {total_pages} pages détectées")

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n\n--- Page {page_num + 1} ---\n\n"
                    text += page_text.strip()

        print(f"✅ Texte extrait : {len(text)} caractères, {len(text.split())} mots")
        return text
    except Exception as e:
        print(f"❌ Erreur extraction PDF : {e}")
        raise