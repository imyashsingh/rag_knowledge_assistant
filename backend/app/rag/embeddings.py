import hashlib
import json
import math
from typing import List, Optional
from app.core.redis_client import redis_client
from app.config import settings


def generate_embedding(text: str) -> List[float]:
    """Generate simple hash-based embedding for text with caching"""
    key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    vec = _generate_simple_embedding(text)
    redis_client.set(key, json.dumps(vec), ex=86400)  # 24 hours
    return vec


def _generate_simple_embedding(text: str) -> List[float]:
    """Generate simple hash-based embedding for text (no ML models)"""
    # Create a simple embedding using multiple hash functions
    embedding = []

    # Use different hash algorithms to create a pseudo-embedding
    hash_functions = [
        lambda x: hashlib.sha256(x.encode()).hexdigest(),
        lambda x: hashlib.md5(x.encode()).hexdigest(),
        lambda x: hashlib.sha1(x.encode()).hexdigest(),
    ]

    # Generate features from text characteristics
    text_length = len(text)
    word_count = len(text.split())
    avg_word_length = sum(len(word)
                          for word in text.split()) / max(word_count, 1)

    # Create embedding vector
    for i in range(384):  # Match typical embedding dimension
        if i < 10:
            # Text statistics
            if i == 0:
                embedding.append(text_length / 1000.0)
            elif i == 1:
                embedding.append(word_count / 100.0)
            elif i == 2:
                embedding.append(avg_word_length / 10.0)
            else:
                embedding.append(0.0)
        else:
            # Hash-based features
            hash_idx = i % len(hash_functions)
            hash_str = hash_functions[hash_idx](text + str(i))
            # Convert hex hash to float
            hash_float = int(hash_str[:8], 16) / (2**32 - 1)
            embedding.append(hash_float)

    # Normalize the embedding
    magnitude = math.sqrt(sum(x*x for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]

    return embedding


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts with caching"""
    embeddings = []
    uncached_texts = []
    uncached_indices = []

    # Check cache first
    for i, text in enumerate(texts):
        key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"
        cached = redis_client.get(key)
        if cached:
            embeddings.append(json.loads(cached))
        else:
            uncached_texts.append(text)
            uncached_indices.append(i)

    # Generate embeddings for uncached texts
    if uncached_texts:
        new_embeddings = [_generate_simple_embedding(
            text) for text in uncached_texts]

        # Cache new embeddings
        for text, embedding in zip(uncached_texts, new_embeddings):
            key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"
            redis_client.set(key, json.dumps(embedding), ex=86400)

        # Insert new embeddings in correct positions
        for idx, embedding in zip(uncached_indices, new_embeddings):
            embeddings.insert(idx, embedding)

    return embeddings


def get_embedding_dimension() -> int:
    """Get the dimension of the embedding model"""
    return 384  # Fixed dimension for simple embeddings
