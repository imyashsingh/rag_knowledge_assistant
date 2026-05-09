from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_current_user, get_current_workspace_id, get_current_user_id, get_db
from app.rag.orchestrator import run_rag_pipeline
from app.services.chat_service import handle_chat_query

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def chat_query(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Process a chat query using RAG pipeline with history persistence"""
    try:
        # Validate query
        if not chat_request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "EMPTY_QUERY",
                    "message": "Query cannot be empty",
                    "field": "query"
                }
            )

        # Process chat query with history persistence
        response = handle_chat_query(
            query=chat_request.query,
            workspace_id=workspace_id,
            user_id=user_id,
            max_sources=chat_request.max_sources,
            db=db,
            session_id=getattr(chat_request, 'session_id', None),
            conversation_history=chat_request.conversation_history
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "QUERY_PROCESSING_FAILED",
                    "message": "Failed to process query",
                    "details": "RAG pipeline returned no response"
                }
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.get("/history", response_model=list)
def get_chat_history_endpoint(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user as a flat list"""
    try:
        from app.db.repositories.chat_history_repo import ChatHistoryRepository
        chat_repo = ChatHistoryRepository(db)
        history = chat_repo.get_user_chat_history(
            user_id=user_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset
        )
        return [
            {
                "id": chat.id,
                "query": chat.query,
                "answer": chat.answer,
                "sources": chat.sources or [],
                "session_id": chat.session_id,
                "created_at": chat.created_at.isoformat(),
                "user_id": chat.user_id,
                "workspace_id": chat.workspace_id,
            }
            for chat in history
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CHAT_HISTORY_FAILED",
                "message": "Failed to get chat history",
                "details": str(e)
            }
        )


@router.get("/stats")
def get_chat_workspace_stats(
    workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Get workspace statistics for chat"""
    try:
        from app.services.chat_service import get_chat_statistics

        stats = get_chat_statistics(workspace_id, db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CHAT_STATS_FAILED",
                "message": "Failed to get workspace statistics",
                "details": str(e)
            }
        )


@router.post("/clear-cache")
def clear_chat_cache(
    workspace_id: int = Depends(get_current_workspace_id)
):
    """Clear RAG cache for the workspace"""
    try:
        from app.rag.orchestrator import clear_rag_cache

        success = clear_rag_cache(workspace_id)

        if success:
            return {"message": "Cache cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear cache"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CACHE_CLEAR_FAILED",
                "message": "Failed to clear cache",
                "details": str(e)
            }
        )


# Legacy endpoint for backward compatibility
@router.post("/legacy")
def legacy_query(
    q: str,
    ws: str,
    user=Depends(lambda: {"user_id": 1})  # Temporary fallback
):
    """Legacy query endpoint - use /query instead"""
    try:
        # Convert to new format
        chat_request = ChatRequest(query=q, max_sources=5)
        workspace_id = int(ws) if ws.isdigit() else 1
        user_id = user.get("user_id", 1)

        response = run_rag_pipeline(
            query=chat_request.query,
            workspace_id=workspace_id,
            user_id=user_id,
            max_sources=chat_request.max_sources
        )

        return response if response else {"error": "Failed to process query"}

    except Exception as e:
        return {
            "error": "LEGACY_QUERY_FAILED",
            "message": "Query processing failed",
            "details": str(e),
            "note": "Please use /query endpoint instead"
        }
