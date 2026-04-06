"""Vector generation module for RVG Project"""

import logging
from src.config import Config

logger = logging.getLogger(__name__)


class VectorGenerator:
    """Generates embeddings for documents"""

    def __init__(self):
        """Initialize VectorGenerator"""
        logger.info(f"VectorGenerator initialized with model: {Config.EMBEDDING_MODEL}")
        self.model_name = Config.EMBEDDING_MODEL

    def generate_vectors(self, documents):
        """Generate vectors for documents"""
        vectors = []

        for doc in documents:
            if doc:
                # Placeholder for actual embedding generation
                vector = {
                    "id": hash(doc["path"]) % (10**8),
                    "path": doc["path"],
                    "content": doc["content"],
                    "embedding": self._generate_embedding(doc["content"]),
                }
                vectors.append(vector)

        logger.info(f"Generated vectors for {len(vectors)} documents")
        return vectors

    def _generate_embedding(self, text):
        """Generate embedding for text (placeholder)"""
        # This is a placeholder. In production, use OpenAI API or similar
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        # Convert to simple vector
        return [int(hash_hex[i : i + 2], 16) / 255.0 for i in range(0, 32, 2)]

    def batch_generate(self, documents, batch_size=32):
        """Generate vectors in batches"""
        vectors = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            vectors.extend(self.generate_vectors(batch))
        return vectors
