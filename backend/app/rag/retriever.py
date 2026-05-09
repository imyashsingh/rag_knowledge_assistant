from typing import List, Tuple, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.rag.embeddings import generate_embedding
from app.db.models.chunk import Chunk
from app.db.models.document import Document


def search_similar_chunks(
    query: str,
    workspace_id: int,
    db: Session,
    limit: int = 5,
    rerank: bool = True
) -> List[Tuple[str, int, str, float]]:
    """
    Search for similar chunks using vector similarity

    Returns:
        List of tuples: (chunk_text, document_id, document_title, similarity_score)
    """
    try:
        query_embedding = generate_embedding(query)

        # Convert embedding to string for PostgreSQL
        embedding_str = str(query_embedding)

        # Enhanced vector search with pgvector
        results = db.execute(text("""
            SELECT 
                c.text,
                c.document_id,
                d.title as document_title,
                1 - (c.embedding <=> :query_embedding) as similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.workspace_id = :workspace_id
            ORDER BY c.embedding <=> :query_embedding
            LIMIT :limit
        """), {
            "query_embedding": embedding_str,
            "workspace_id": workspace_id,
            "limit": limit * 2 if rerank else limit  # Get more for reranking
        }).fetchall()

        # Convert to list of tuples
        search_results = []
        for row in results:
            chunk_text, document_id, document_title, similarity = row
            search_results.append(
                (chunk_text, document_id, document_title, float(similarity)))

        # Apply reranking if enabled
        if rerank and len(search_results) > 1:
            search_results = _rerank_results(query, search_results)

        # Return top results
        return search_results[:limit]
    except Exception as e:
        raise Exception(f"Vector search failed: {str(e)}")


def _rerank_results(
    query: str,
    results: List[Tuple[str, int, str, float]]
) -> List[Tuple[str, int, str, float]]:
    """
    Enhanced reranking based on keyword overlap, semantic similarity, and position relevance
    """
    query_words = set(query.lower().split())

    reranked = []
    for idx, (chunk_text, document_id, document_title, similarity) in enumerate(results):
        chunk_words = set(chunk_text.lower().split())

        # Keyword overlap score (40%)
        keyword_overlap = len(query_words & chunk_words) / \
            len(query_words | chunk_words) if query_words else 0

        # Position boost (earlier chunks get slight boost)
        position_boost = 1.0 - (idx * 0.05)  # 5% boost for first position

        # Length penalty (very short or very long chunks penalized)
        chunk_length = len(chunk_text.split())
        length_penalty = 1.0
        if chunk_length < 20:  # Too short
            length_penalty = 0.8
        elif chunk_length > 500:  # Too long
            length_penalty = 0.9

        # Combined score (50% semantic, 40% keyword, 10% position)
        combined_score = (
            0.5 * similarity +
            0.4 * keyword_overlap +
            0.1 * position_boost
        ) * length_penalty

        reranked.append(
            (chunk_text, document_id, document_title, combined_score))

    # Sort by combined score
    reranked.sort(key=lambda x: x[3], reverse=True)
    return reranked


def get_document_chunks(document_id: int, workspace_id: int, db: Session) -> List[Chunk]:
    """Get all chunks for a specific document"""
    return db.query(Chunk).filter(
        Chunk.document_id == document_id,
        Chunk.workspace_id == workspace_id
    ).order_by(Chunk.chunk_index).all()


def get_workspace_document_count(workspace_id: int, db: Session) -> int:
    """Get count of documents in workspace"""
    return db.query(Document).filter(Document.workspace_id == workspace_id).count()
