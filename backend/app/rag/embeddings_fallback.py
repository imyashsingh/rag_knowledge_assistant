import hashlib
import json
import math
from typing import List, Optional
from app.core.redis_client import redis_client

def generate_embedding(text: str) -> List[float]:
    """Generate simple hash-based embedding for testing"""
    key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    # Create a simple 384-dimensional embedding (matching original)
    embedding = []
    hash_functions = [
        lambda x: hashlib.sha256(x.encode()).hexdigest(),
        lambda x: hashlib.md5(x.encode()).hexdigest(),
        lambda x: hashlib.sha1(x.encode()).hexdigest(),
    ]

    text_length = len(text)
    word_count = len(text.split())
    avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)

    for i in range(384):  # Match original embedding dimension
        if i < 3:
            if i == 0:
                embedding.append(text_length / 1000.0)
            elif i == 1:
                embedding.append(word_count / 100.0)
            elif i == 2:
                embedding.append(avg_word_length / 10.0)
            else:
                embedding.append(0.0)
        else:
            hash_idx = i % len(hash_functions)
            hash_str = hash_functions[hash_idx](text + str(i))
            hash_float = int(hash_str[:8], 16) / (2**32 - 1)
            embedding.append(hash_float)

    # Normalize the embedding
    magnitude = math.sqrt(sum(x*x for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]

    # Cache for 24 hours
    redis_client.set(key, json.dumps(embedding), ex=86400)
    return embedding


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts with caching"""
    return [generate_embedding(text) for text in texts]


def get_embedding_dimension() -> int:
    """Get the dimension of the embedding model"""
    return 384


def validate_embedding_model() -> bool:
    """Test if the embedding model is working properly"""
    try:
        test_embedding = generate_embedding("test text")
        return len(test_embedding) == get_embedding_dimension()
    except Exception as e:
        print(f"Embedding model validation failed: {str(e)}")
        return False
