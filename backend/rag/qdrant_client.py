from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import settings
from rag.embeddings import VECTOR_SIZE

COLLECTION = "agri_knowledge"

class QdrantManager:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    async def ensure_collection(self):
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]
        if COLLECTION not in names:
            await self.client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            print(f"Created collection: {COLLECTION}")

    async def upsert_documents(self, docs: List[Dict[str, Any]], embeddings: List[List[float]]):
        points = [
            PointStruct(id=i, vector=emb, payload=doc)
            for i, (doc, emb) in enumerate(zip(docs, embeddings))
        ]
        await self.client.upsert(collection_name=COLLECTION, points=points)
        return len(points)

    async def search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        results = await self.client.search(
            collection_name=COLLECTION, query_vector=query_vector, limit=limit
        )
        return [{"text": r.payload.get("text", ""), "source": r.payload.get("source", ""), "score": r.score} for r in results]
