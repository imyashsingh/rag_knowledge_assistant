from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.rag.orchestrator import run_rag_pipeline
from app.schemas.chat import ChatResponse
from app.core.exceptions import RAGException
from app.db.repositories.chat_history_repo import ChatHistoryRepository


def handle_chat_query(
    query: str,
    workspace_id: int,
    user_id: int,
    max_sources: int = 5,
    db: Session = None,
    session_id: str = None,
    conversation_history: list = None
) -> Optional[ChatResponse]:
    """
    Handle chat query using RAG pipeline with history persistence

    Args:
        query: User's question
        workspace_id: Workspace ID for isolation
        user_id: User ID for tracking
        max_sources: Maximum number of sources to retrieve
        db: Database session for history persistence
        session_id: Optional session ID for conversation grouping

    Returns:
        ChatResponse with answer and sources, or None if error
    """
    try:
        if not query.strip():
            raise RAGException("Query cannot be empty")

        response = run_rag_pipeline(
            query=query,
            workspace_id=workspace_id,
            user_id=user_id,
            max_sources=max_sources,
            db=db,
            conversation_history=conversation_history
        )

        # Save chat history if database session is provided
        if db and response:
            try:
                chat_repo = ChatHistoryRepository(db)
                chat_repo.create_chat_entry(
                    user_id=user_id,
                    workspace_id=workspace_id,
                    query=query,
                    answer=response.answer,
                    sources=[source.model_dump()
                             for source in response.sources],
                    session_id=session_id
                )
            except Exception as db_error:
                # Rollback any failed transaction and continue without saving history
                db.rollback()
                print(f"Warning: Failed to save chat history: {db_error}")

        return response
    except Exception as e:
        raise RAGException(f"Chat query failed: {str(e)}")


def get_chat_history(
    workspace_id: int,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = None
) -> Dict[str, Any]:
    """
    Get chat history for a user in a workspace
    """
    if not db:
        return {
            "message": "Database session required",
            "workspace_id": workspace_id,
            "user_id": user_id,
            "limit": limit
        }

    try:
        chat_repo = ChatHistoryRepository(db)
        history = chat_repo.get_user_chat_history(
            user_id=user_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset
        )

        return {
            "history": [
                {
                    "id": chat.id,
                    "query": chat.query,
                    "answer": chat.answer,
                    "sources": chat.sources,
                    "session_id": chat.session_id,
                    "created_at": chat.created_at.isoformat()
                }
                for chat in history
            ],
            "workspace_id": workspace_id,
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise RAGException(f"Failed to get chat history: {str(e)}")


def get_chat_statistics(workspace_id: int, db: Session = None) -> Dict[str, Any]:
    """Get chat statistics for a workspace"""
    try:
        from app.rag.orchestrator import get_workspace_stats

        if not db:
            return {
                "error": "Database session required for statistics",
                "workspace_id": workspace_id
            }

        stats = get_workspace_stats(workspace_id, db)

        # Add chat-specific statistics
        stats.update({
            "total_queries": 0,  # Would need to implement query tracking
            "average_response_time": 0.0,  # Would need to implement timing
            "cache_hit_rate": 0.0  # Would need to implement cache tracking
        })

        return stats
    except Exception as e:
        raise RAGException(f"Failed to get chat statistics: {str(e)}")


def clear_chat_cache(workspace_id: int) -> bool:
    """Clear chat cache for a workspace"""
    try:
        from app.rag.orchestrator import clear_rag_cache
        return clear_rag_cache(workspace_id)
    except Exception as e:
        raise RAGException(f"Failed to clear chat cache: {str(e)}")


# Legacy function for backward compatibility
def handle_query(q: str, ws: str, uid: int):
    """Legacy function - use handle_chat_query instead"""
    try:
        # Convert legacy parameters to new format
        workspace_id = int(ws.replace("ws", "")) if isinstance(ws, str) else ws

        response = run_rag_pipeline(
            query=q,
            workspace_id=workspace_id,
            user_id=uid,
            max_sources=5
        )

        if response:
            return {
                "answer": response.answer,
                "sources": [
                    {
                        "document_id": src.document_id,
                        "document_title": src.document_title,
                        "chunk_text": src.chunk_text,
                        "relevance_score": src.relevance_score
                    }
                    for src in response.sources
                ]
            }
        else:
            return {"error": "Failed to process query"}

    except Exception as e:
        return {"error": f"Query processing failed: {str(e)}"}
