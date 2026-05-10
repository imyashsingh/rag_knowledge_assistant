from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.workspace import Workspace
from app.db.models.user import User
from app.db.models.chat_history import ChatHistory
from app.db.repositories.base_repo import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db_session: Session):
        super().__init__(Workspace, db_session)

    def get_by_name(self, name: str) -> Optional[Workspace]:
        return self.get_by_field("name", name)

    def get_by_owner(self, owner_id: int) -> List[Workspace]:
        """Get all workspaces owned by a specific user"""
        return (
            self.db_session.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .all()
        )

    def create_workspace(self, name: str, owner_id: int) -> Workspace:
        return self.create(name=name, owner_id=owner_id)

    def get_all(self) -> List[Workspace]:
        """Get all workspaces"""
        return self.get_multi()

    def get_with_users(self, workspace_id: int) -> Optional[Workspace]:
        return (
            self.db_session.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace and all associated data"""
        try:
            # Get all users in this workspace
            users_in_workspace = self.db_session.query(User).filter(
                User.workspace_id == workspace_id
            ).all()

            # Delete chat history for all users in this workspace
            if users_in_workspace:
                user_ids = [user.id for user in users_in_workspace]
                self.db_session.query(ChatHistory).filter(
                    ChatHistory.user_id.in_(user_ids)
                ).delete()

            # Delete users associated with this workspace
            self.db_session.query(User).filter(
                User.workspace_id == workspace_id
            ).delete()

            # Delete the workspace (cascade will handle documents and chunks)
            db_obj = self.get_by_id(workspace_id)
            if db_obj:
                self.db_session.delete(db_obj)
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            raise e
