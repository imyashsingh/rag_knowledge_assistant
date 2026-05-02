from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_current_user, get_current_workspace_id, get_current_user_id
from app.rag.orchestrator import run_rag_pipeline, get_workspace_stats
from app.services.chat_service import handle_chat_query

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def chat_query(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id)
):
    """Process a chat query using RAG pipeline"""
    try:
        # Validate query
        if not chat_request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        # Run RAG pipeline
        response = run_rag_pipeline(
            query=chat_request.query,
            workspace_id=workspace_id,
            user_id=user_id,
            max_sources=chat_request.max_sources
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process query"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.get("/stats")
def get_chat_workspace_stats(
    workspace_id: int = Depends(get_current_workspace_id)
):
    """Get workspace statistics for chat"""
    try:
        stats = get_workspace_stats(workspace_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workspace statistics"
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
            detail=f"Cache clearing failed: {str(e)}"
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
        return {"error": f"Query processing failed: {str(e)}"}
