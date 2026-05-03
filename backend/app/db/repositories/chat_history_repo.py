from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db.models.chat_history import ChatHistory
from app.db.repositories.base_repo import BaseRepository


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self, db_session: Session):
        super().__init__(ChatHistory, db_session)

    def create_chat_entry(
        self,
        user_id: int,
        workspace_id: int,
        query: str,
        answer: str,
        sources: dict = None,
        session_id: str = None
    ) -> ChatHistory:
        return self.create(
            user_id=user_id,
            workspace_id=workspace_id,
            query=query,
            answer=answer,
            sources=sources,
            session_id=session_id
        )

    def get_user_chat_history(
        self,
        user_id: int,
        workspace_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistory]:
        return (
            self.db_session.query(ChatHistory)
            .filter(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.workspace_id == workspace_id
                )
            )
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_workspace_chat_history(
        self,
        workspace_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatHistory]:
        return (
            self.db_session.query(ChatHistory)
            .filter(ChatHistory.workspace_id == workspace_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_session_chat_history(
        self,
        user_id: int,
        workspace_id: int,
        session_id: str,
        limit: int = 20
    ) -> List[ChatHistory]:
        return (
            self.db_session.query(ChatHistory)
            .filter(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.workspace_id == workspace_id,
                    ChatHistory.session_id == session_id
                )
            )
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
            .all()
        )

    def delete_user_chat_history(
        self,
        user_id: int,
        workspace_id: int
    ) -> int:
        deleted_count = (
            self.db_session.query(ChatHistory)
            .filter(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.workspace_id == workspace_id
                )
            )
            .delete()
        )
        self.db_session.commit()
        return deleted_count

    def get_chat_statistics(
        self,
        workspace_id: int,
        user_id: Optional[int] = None
    ) -> dict:
        query = self.db_session.query(ChatHistory).filter(
            ChatHistory.workspace_id == workspace_id
        )
        
        if user_id:
            query = query.filter(ChatHistory.user_id == user_id)
        
        total_chats = query.count()
        
        return {
            "total_chats": total_chats,
            "workspace_id": workspace_id,
            "user_id": user_id
        }
