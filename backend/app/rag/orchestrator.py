from typing import Dict, Any, Optional
import hashlib
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.rag.retriever import search_similar_chunks
from app.rag.llm import generate_chat_response
from app.core.redis_client import redis_client
from app.schemas.chat import ChatResponse, SourceDocument


def run_rag_pipeline(
    query: str,
    workspace_id: int,
    user_id: int,
    max_sources: int = 5,
    db: Session = None
) -> Optional[ChatResponse]:
    """
    Run complete RAG pipeline with caching

    Args:
        query: User's question
        workspace_id: Workspace ID for isolation
        user_id: User ID for tracking
        max_sources: Maximum number of sources to retrieve
        db: Database session (optional, will create if not provided)

    Returns:
        ChatResponse with answer and sources, or None if error
    """
    try:
        # Check cache first
        cache_key = f"rag:{hashlib.md5(f'{query}:{workspace_id}'.encode()).hexdigest()}"
        cached_response = redis_client.get(cache_key)
        if cached_response:
            cached_data = json.loads(cached_response)
            return ChatResponse(**cached_data)

        # Use provided db session or create temporary one
        if db is None:
            db = SessionLocal()
            should_close_db = True
        else:
            should_close_db = False

        try:
            # Retrieve relevant chunks
            search_results = search_similar_chunks(
                query=query,
                workspace_id=workspace_id,
                db=db,
                limit=max_sources,
                rerank=True
            )

            if not search_results:
                return ChatResponse(
                    answer="I don't have enough information to answer this question based on the available documents.",
                    sources=[],
                    query=query
                )

            # Extract context chunks and source information
            context_chunks = []
            sources = []

            for chunk_text, document_id, document_title, similarity_score in search_results:
                context_chunks.append(chunk_text)
                sources.append(SourceDocument(
                    document_id=document_id,
                    document_title=document_title,
                    chunk_text=chunk_text,
                    relevance_score=similarity_score
                ))

            # Generate response
            answer = generate_chat_response(query, context_chunks)

            if not answer:
                return ChatResponse(
                    answer="I encountered an error while generating a response. Please try again.",
                    sources=sources,
                    query=query
                )

            response = ChatResponse(
                answer=answer,
                sources=sources,
                query=query
            )

            # Cache response for 5 minutes
            redis_client.set(cache_key, response.model_dump_json(), ex=300)

            return response

        finally:
            # Close database session if we created it
            if should_close_db:
                db.close()

    except Exception as e:
        print(f"Error in RAG pipeline: {str(e)}")
        return ChatResponse(
            answer="I encountered an error while processing your question. Please try again.",
            sources=[],
            query=query
        )


def get_workspace_stats(workspace_id: int, db: Session) -> Dict[str, Any]:
    """Get statistics about workspace documents and chunks"""
    try:
        doc_count = get_workspace_document_count(workspace_id, db)

        return {
            "document_count": doc_count,
            "workspace_id": workspace_id
        }
    except Exception as e:
        print(f"Error getting workspace stats: {str(e)}")
        return {"document_count": 0, "workspace_id": workspace_id}


def clear_rag_cache(workspace_id: Optional[int] = None) -> bool:
    """Clear RAG cache for workspace or all"""
    try:
        if workspace_id:
            # Clear specific workspace cache (implementation depends on your Redis key strategy)
            pattern = f"rag:*{workspace_id}*"
        else:
            # Clear all RAG cache
            pattern = "rag:*"

        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Error clearing RAG cache: {str(e)}")
        return False
