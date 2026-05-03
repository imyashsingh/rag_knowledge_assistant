import hashlib
import json
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.redis_client import redis_client

# Load the sentence transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using sentence transformer model"""
    key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"

    # Check cache first
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    # Generate embedding using sentence transformer
    embedding = model.encode(text, normalize_embeddings=True)

    # Convert numpy array to list
    embedding_list = embedding.tolist()

    # Cache the embedding
    redis_client.setex(key, 86400, json.dumps(
        embedding_list))  # Cache for 24 hours

    return embedding_list


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
