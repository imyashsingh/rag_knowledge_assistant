from typing import Dict, Any, Optional
import hashlib
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.rag.retriever import search_similar_chunks
from app.rag.llm import generate_chat_response
from app.core.redis_client import redis_client
from app.schemas.chat import ChatResponse, SourceDocument
from app.db.repositories.document_repo import DocumentRepository


def run_rag_pipeline(
    query: str,
    workspace_id: int,
    user_id: int,
    max_sources: int = 5,
    db: Session = None,
    conversation_history: list = None
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
        # Get workspace document count for cache versioning
        db_session = db or SessionLocal()
        should_close_db = db is None

        try:
            doc_repo = DocumentRepository(db_session)
            doc_count = len(doc_repo.get_by_workspace(workspace_id))
        finally:
            if should_close_db:
                db_session.close()

        # Track query frequency for smart caching
        track_query_frequency(workspace_id, query)

        # Check cache first with workspace versioning
        cache_key = f"rag:{workspace_id}:{doc_count}:{hashlib.md5(query.encode()).hexdigest()}"
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
            answer = generate_chat_response(
                query, context_chunks, conversation_history)

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

            # Cache response for 5 minutes with size limit check
            cache_size = get_workspace_cache_size(workspace_id)
            query_freq = get_query_frequency(workspace_id, query)

            # Only cache frequently asked questions (frequency > 1) or if under size limit
            if cache_size < 1000 or query_freq > 1:
                redis_client.set(cache_key, response.model_dump_json(), ex=300)
                increment_workspace_cache_count(workspace_id)

            return response

        finally:
            # Close database session if we created it
            if should_close_db:
                db.close()

    except Exception as e:
        print(f"Error in RAG pipeline: {str(e)}")
        # Include error details in the response for debugging
        error_message = f"I encountered an error while processing your question: {str(e)}. Please try again."
        return ChatResponse(
            answer=error_message,
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
            # Clear specific workspace cache
            pattern = f"rag:{workspace_id}:*"
            # Reset workspace cache count
            redis_client.delete(f"cache_count:workspace:{workspace_id}")
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


def get_workspace_cache_size(workspace_id: int) -> int:
    """Get current cache size for workspace"""
    try:
        count = redis_client.get(f"cache_count:workspace:{workspace_id}")
        return int(count) if count else 0
    except:
        return 0


def increment_workspace_cache_count(workspace_id: int):
    """Increment workspace cache count"""
    try:
        redis_client.incr(f"cache_count:workspace:{workspace_id}")
        redis_client.expire(
            f"cache_count:workspace:{workspace_id}", 86400)  # 24 hours
    except:
        pass


def track_query_frequency(workspace_id: int, query: str):
    """Track how often queries are asked"""
    try:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"query_freq:{workspace_id}:{query_hash}"
        redis_client.incr(key)
        redis_client.expire(key, 86400)  # Track for 24 hours
    except:
        pass


def get_query_frequency(workspace_id: int, query: str) -> int:
    """Get how many times a query was asked"""
    try:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"query_freq:{workspace_id}:{query_hash}"
        freq = redis_client.get(key)
        return int(freq) if freq else 0
    except:
        return 0
