from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models.user import User
from app.db.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.get_by_field("email", email)

    def create_user(self, email: str, password: str, workspace_id: int, name: str) -> User:
        return self.create(email=email, password=password, workspace_id=workspace_id, name=name)

    def get_workspace_users(self, workspace_id: int) -> List[User]:
        return self.get_by_workspace(workspace_id)

    def get_by_email_and_workspace(self, email: str, workspace_id: int) -> Optional[User]:
        return (
            self.db_session.query(User)
            .filter(and_(User.email == email, User.workspace_id == workspace_id))
            .first()
        )
