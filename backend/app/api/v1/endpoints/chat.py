from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_current_user, get_current_workspace_id, get_current_user_id, get_db
from app.rag.orchestrator import run_rag_pipeline
from app.services.chat_service import handle_chat_query
from app.db.repositories.chat_history_repo import ChatHistoryRepository

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
            session_id=chat_request.session_id,
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


@router.post("/sessions")
def create_session(
    session_data: dict,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new chat session with optional name"""
    try:
        session_id = session_data.get("session_id")
        session_name = session_data.get("name")

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session ID is required"
            )

        # Create a placeholder chat entry to establish the session with name
        if session_name:
            chat_repo = ChatHistoryRepository(db)
            # Create a minimal entry to establish the session with name
            from sqlalchemy import text
            db.execute(
                text("""
                INSERT INTO chat_history (user_id, workspace_id, session_id, name, query, answer, created_at)
                VALUES (:user_id, :workspace_id, :session_id, :name, :query, :answer, NOW())
                """),
                {
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "session_id": session_id,
                    "name": session_name,
                    "query": "[Session Created]",
                    "answer": "[Session Started]",
                }
            )
            db.commit()

        return {"session_id": session_id, "name": session_name}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SESSION_CREATE_FAILED",
                "message": "Failed to create session",
                "details": str(e)
            }
        )


@router.get("/sessions")
def get_chat_sessions(
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current workspace"""
    try:
        chat_repo = ChatHistoryRepository(db)

        # Get all chat history for this workspace/user
        all_chats = chat_repo.get_user_chat_history(
            user_id, workspace_id, limit=1000)

        # Group by session_id and create session metadata
        sessions_dict = {}
        for chat in all_chats:
            session_id = chat.session_id
            if not session_id:
                continue

            if session_id not in sessions_dict:
                # Use custom name from database if available, otherwise generate default
                custom_name = getattr(chat, 'name', None)
                if custom_name and custom_name.strip():
                    session_name = custom_name
                else:
                    short_id = session_id.replace('session-', '')[:8].upper()
                    session_name = f"New Chat {short_id}"

                sessions_dict[session_id] = {
                    "session_id": session_id,
                    "message_count": 0,
                    "last_message_at": chat.created_at,
                    "created_at": chat.created_at,
                    "name": session_name
                }

            # Skip placeholder entries in message count
            if chat.query != "[Session Created]":
                sessions_dict[session_id]["message_count"] += 1

            # Update last_message_at if this chat is newer
            if chat.created_at > sessions_dict[session_id]["last_message_at"]:
                sessions_dict[session_id]["last_message_at"] = chat.created_at

        # Convert to list and update names with message count
        sessions_list = list(sessions_dict.values())

        # Update session names to include message count only for default/auto-generated names
        for session in sessions_list:
            current_name = session["name"]
            # Only modify auto-generated names (those starting with "New Chat" or "Chat")
            if current_name and (current_name.startswith("New Chat") or
                                 (current_name.startswith("Chat ") and "message" in current_name)):
                message_count = session["message_count"]
                short_id = session['session_id'].replace(
                    'session-', '')[:8].upper()

                if message_count == 1:
                    session["name"] = f"Chat {short_id} (1 message)"
                elif message_count > 1:
                    session["name"] = f"Chat {short_id} ({message_count} messages)"

        sessions_list.sort(key=lambda x: x["last_message_at"], reverse=True)

        return sessions_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SESSIONS_FETCH_FAILED",
                "message": "Failed to fetch chat sessions",
                "details": str(e)
            }
        )


@router.get("/search")
def search_chat_history(
    q: str,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """Search chat history"""
    try:
        if not q.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )

        chat_repo = ChatHistoryRepository(db)

        # Build query
        query = db.session.query(chat_repo.model).filter(
            chat_repo.model.workspace_id == workspace_id,
            chat_repo.model.user_id == user_id,
            chat_repo.model.query.ilike(f"%{q}%")
        )

        if session_id:
            query = query.filter(chat_repo.model.session_id == session_id)

        results = query.order_by(
            desc(chat_repo.model.created_at)).limit(50).all()

        return [
            {
                "id": chat.id,
                "session_id": chat.session_id,
                "query": chat.query,
                "answer": chat.answer,
                "created_at": chat.created_at,
                "sources": chat.sources or []
            }
            for chat in results
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SEARCH_FAILED",
                "message": "Failed to search chat history",
                "details": str(e)
            }
        )


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    try:
        chat_repo = ChatHistoryRepository(db)

        # Delete all chat entries for this session
        from sqlalchemy import delete
        delete_stmt = delete(chat_repo.model).where(
            chat_repo.model.session_id == session_id,
            chat_repo.model.user_id == user_id,
            chat_repo.model.workspace_id == workspace_id
        )

        result = db.execute(delete_stmt)
        db.commit()

        return {"message": f"Session {session_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SESSION_DELETE_FAILED",
                "message": "Failed to delete session",
                "details": str(e)
            }
        )


@router.patch("/sessions/{session_id}")
def update_session_name(
    session_id: str,
    name_data: dict,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update session name"""
    try:
        if not name_data.get("name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session name cannot be empty"
            )

        chat_repo = ChatHistoryRepository(db)

        # Get all chats for this session
        chats = db.query(chat_repo.model).filter(
            chat_repo.model.session_id == session_id,
            chat_repo.model.user_id == user_id,
            chat_repo.model.workspace_id == workspace_id
        ).all()

        if not chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Update all chats in this session with the new name
        from sqlalchemy import update
        update_stmt = update(chat_repo.model).where(
            chat_repo.model.session_id == session_id,
            chat_repo.model.user_id == user_id,
            chat_repo.model.workspace_id == workspace_id
        ).values(name=name_data["name"])

        db.execute(update_stmt)
        db.commit()

        return {"message": "Session name updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SESSION_UPDATE_FAILED",
                "message": "Failed to update session name",
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
