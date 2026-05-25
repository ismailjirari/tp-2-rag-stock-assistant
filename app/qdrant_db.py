# qdrant_db.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import (
    QDRANT_URL, QDRANT_API_KEY,
    COLLECTION_NAME, EMBEDDING_DIMENSION, TOP_K
)

# Connexion avec timeout augmenté
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120  # 120 secondes au lieu de 30 par défaut
)


def create_collection(collection_name: str = COLLECTION_NAME):
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        print(f"⚠️  Collection '{collection_name}' existe déjà.")
        return
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE
        )
    )
    print(f"✅ Collection '{collection_name}' créée.")


def upload_vectors(chunks: list[dict], vectors: list[list[float]], collection_name: str = COLLECTION_NAME):
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload={
                    "chunk": chunk["chunk"],
                    "id": chunk["id"]
                }
            )
        )

    # Batch réduit à 10 points pour éviter le timeout
    batch_size = 10
    total = len(points)

    for i in range(0, total, batch_size):
        batch = points[i:i + batch_size]
        success = False
        retries = 3

        while not success and retries > 0:
            try:
                client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                print(f"⬆️  Batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size} uploadé ({len(batch)} points)")
                success = True
            except Exception as e:
                retries -= 1
                print(f"⚠️  Erreur batch {i // batch_size + 1}, tentative restante : {retries} | {e}")
                if retries == 0:
                    raise

    print(f"✅ {total} vecteurs uploadés dans '{collection_name}'.")


def search_vectors(query_vector: list[float], top_k: int = TOP_K, collection_name: str = COLLECTION_NAME) -> list[dict]:
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True
    ).points

    retrieved = []
    for hit in results:
        retrieved.append({
            "chunk": hit.payload.get("chunk", ""),
            "score": hit.score,
            "id": hit.payload.get("id", hit.id)
        })
    return retrieved


def delete_collection(collection_name: str = COLLECTION_NAME):
    client.delete_collection(collection_name=collection_name)
    print(f"🗑️  Collection '{collection_name}' supprimée.")


def get_collection_info(collection_name: str = COLLECTION_NAME):
    info = client.get_collection(collection_name=collection_name)
    print(f"📊 Collection : {collection_name}")
    print(f"   Points     : {info.points_count}")
    print(f"   Status     : {info.status}")
    return info