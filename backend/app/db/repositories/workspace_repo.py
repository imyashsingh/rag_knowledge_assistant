from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.workspace import Workspace
from app.db.repositories.base_repo import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db_session: Session):
        super().__init__(Workspace, db_session)

    def get_by_name(self, name: str) -> Optional[Workspace]:
        return self.get_by_field("name", name)

    def create_workspace(self, name: str) -> Workspace:
        return self.create(name=name)

    def get_all(self) -> List[Workspace]:
        """Get all workspaces"""
        return self.get_multi()

    def get_with_users(self, workspace_id: int) -> Optional[Workspace]:
        return (
            self.db_session.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )
