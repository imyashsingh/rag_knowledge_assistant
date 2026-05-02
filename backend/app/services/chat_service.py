from typing import Optional, Dict, Any
from app.rag.orchestrator import run_rag_pipeline
from app.schemas.chat import ChatResponse
from app.core.exceptions import RAGException


def handle_chat_query(
    query: str,
    workspace_id: int,
    user_id: int,
    max_sources: int = 5
) -> Optional[ChatResponse]:
    """
    Handle chat query using RAG pipeline

    Args:
        query: User's question
        workspace_id: Workspace ID for isolation
        user_id: User ID for tracking
        max_sources: Maximum number of sources to retrieve

    Returns:
        ChatResponse with answer and sources, or None if error
    """
    try:
        if not query.strip():
            raise RAGException("Query cannot be empty")

        return run_rag_pipeline(
            query=query,
            workspace_id=workspace_id,
            user_id=user_id,
            max_sources=max_sources
        )
    except Exception as e:
        raise RAGException(f"Chat query failed: {str(e)}")


def get_chat_history(
    workspace_id: int,
    user_id: int,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get chat history for a user in a workspace
    (This would require implementing a chat history table)
    """
    # Placeholder for chat history functionality
    return {
        "message": "Chat history not implemented yet",
        "workspace_id": workspace_id,
        "user_id": user_id,
        "limit": limit
    }


def get_chat_statistics(workspace_id: int) -> Dict[str, Any]:
    """Get chat statistics for a workspace"""
    try:
        from app.rag.orchestrator import get_workspace_stats

        stats = get_workspace_stats(workspace_id)

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
