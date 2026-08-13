from functools import lru_cache
from typing import List

@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("BAAI/bge-small-en-v1.5")

class EmbeddingModel:
    def __init__(self):
        self.model = _load_model()

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()

VECTOR_SIZE = 384
