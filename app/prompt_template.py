# prompt_template.py

SYSTEM_PROMPT = """
Tu es un assistant expert en standards textiles biologiques, spécialisé dans le 
Global Organic Textile Standard (GOTS) version 7.0.

Ton rôle est d'aider les utilisateurs à comprendre et appliquer les exigences 
du standard GOTS : certifications, critères écologiques et sociaux, chaîne de 
traçabilité, étiquetage, et processus de conformité.

Règles importantes :
- Réponds uniquement en te basant sur le contexte fourni.
- Si l'information n'est pas dans le contexte, dis clairement que tu ne sais pas.
- Sois précis, structuré et professionnel.
- Réponds dans la même langue que la question posée.
- Cite les sections ou articles GOTS pertinents quand c'est possible.
"""


def build_rag_prompt(question: str, context_chunks: list[dict]) -> str:
    """
    Construit le prompt RAG avec la question et le contexte récupéré.
    
    Args:
        question: La question de l'utilisateur
        context_chunks: Liste de dicts avec clé 'chunk' et 'score'
    
    Returns:
        Le prompt formaté
    """
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        score = chunk.get("score", 0)
        context_text += f"\n--- Extrait {i} (pertinence: {score:.2f}) ---\n"
        context_text += chunk["chunk"]
        context_text += "\n"

    prompt = f"""
Contexte extrait du document GOTS 7.0 :
{context_text}

---

Question de l'utilisateur :
{question}

---

En te basant UNIQUEMENT sur le contexte ci-dessus, réponds de manière précise 
et structurée à la question. Si le contexte ne contient pas l'information 
nécessaire, indique-le clairement.
"""
    return prompt.strip()