from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.document import Document
from app.db.repositories.base_repo import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db_session: Session):
        super().__init__(Document, db_session)

    def create_document(
        self, 
        title: str, 
        filename: str, 
        content_type: str, 
        workspace_id: int
    ) -> Document:
        return self.create(
            title=title,
            filename=filename,
            content_type=content_type,
            workspace_id=workspace_id
        )

    def get_workspace_documents(self, workspace_id: int) -> List[Document]:
        return self.get_by_workspace(workspace_id)

    def get_by_filename(self, filename: str, workspace_id: int) -> Optional[Document]:
        return (
            self.db_session.query(Document)
            .filter(
                Document.filename == filename,
                Document.workspace_id == workspace_id
            )
            .first()
        )

    def get_with_chunks(self, document_id: int, workspace_id: int) -> Optional[Document]:
        return (
            self.db_session.query(Document)
            .filter(
                Document.id == document_id,
                Document.workspace_id == workspace_id
            )
            .first()
        )
