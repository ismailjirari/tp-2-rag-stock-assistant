# main.py

import os
import sys
from config import PDF_FILE, COLLECTION_NAME
from utils import extract_text_from_pdf, clean_text, split_text, save_chunks, load_chunks
from embeddings import embed_documents, save_embeddings, load_embeddings
from qdrant_db import create_collection, upload_vectors, get_collection_info
from rag_pipeline import ask_question


def ingest_pipeline():
    """Pipeline complet d'ingestion : PDF → chunks → embeddings → Qdrant."""
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE PIPELINE D'INGESTION")
    print("="*60)

    # 1. Extraction texte PDF
    print("\n📄 Étape 1 : Extraction du texte PDF...")
    raw_text = extract_text_from_pdf(PDF_FILE)

    # 2. Nettoyage
    print("\n🧹 Étape 2 : Nettoyage du texte...")
    clean = clean_text(raw_text)

    # 3. Chunking
    print("\n✂️  Étape 3 : Découpage en chunks...")
    raw_chunks = split_text(clean)
    chunks = [{"chunk": c, "id": i} for i, c in enumerate(raw_chunks)]
    print(f"   → {len(chunks)} chunks créés")

    # 4. Sauvegarde chunks
    save_chunks(chunks)

    # 5. Génération embeddings
    print("\n🔢 Étape 4 : Génération des embeddings...")
    texts = [c["chunk"] for c in chunks]
    vectors = embed_documents(texts)
    save_embeddings(vectors)

    # 6. Création collection Qdrant
    print(f"\n🗄️  Étape 5 : Création collection Qdrant '{COLLECTION_NAME}'...")
    create_collection()

    # 7. Upload vers Qdrant
    print("\n⬆️  Étape 6 : Upload vers Qdrant...")
    upload_vectors(chunks, vectors)

    # 8. Vérification
    print("\n📊 Étape 7 : Vérification...")
    get_collection_info()

    print("\n" + "="*60)
    print("✅ INGESTION TERMINÉE AVEC SUCCÈS !")
    print("="*60)


def chat_mode():
    """Mode chat interactif en ligne de commande."""
    print("\n" + "="*60)
    print("💬 MODE CHAT - RAG Stock Assistant (GOTS 7.0)")
    print("   Tapez 'quit' ou 'exit' pour quitter")
    print("="*60 + "\n")

    while True:
        try:
            question = input("❓ Question : ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir !")
                break

            print("\n⏳ Traitement en cours...\n")
            result = ask_question(question)

            print("📝 RÉPONSE :")
            print("-" * 40)
            print(result["answer"])
            print("\n📚 SOURCES UTILISÉES :")
            for i, src in enumerate(result["sources"], 1):
                print(f"  [{i}] Score: {src['score']:.3f} | {src['chunk'][:100]}...")
            print("\n" + "="*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur : {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        ingest_pipeline()
    else:
        chat_mode()