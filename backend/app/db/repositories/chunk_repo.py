from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models.chunk import Chunk
from app.db.repositories.base_repo import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):
    def __init__(self, db_session: Session):
        super().__init__(Chunk, db_session)

    def create_chunk(
        self,
        text: str,
        embedding: list,
        workspace_id: int,
        document_id: int,
        chunk_index: int
    ) -> Chunk:
        return self.create(
            text=text,
            embedding=embedding,
            workspace_id=workspace_id,
            document_id=document_id,
            chunk_index=chunk_index
        )

    def get_document_chunks(self, document_id: int, workspace_id: int) -> List[Chunk]:
        return (
            self.db_session.query(Chunk)
            .filter(
                Chunk.document_id == document_id,
                Chunk.workspace_id == workspace_id
            )
            .order_by(Chunk.chunk_index)
            .all()
        )

    def get_workspace_chunks(self, workspace_id: int) -> List[Chunk]:
        return self.get_by_workspace(workspace_id)

    def delete_document_chunks(self, document_id: int, workspace_id: int) -> int:
        deleted_count = (
            self.db_session.query(Chunk)
            .filter(
                Chunk.document_id == document_id,
                Chunk.workspace_id == workspace_id
            )
            .delete()
        )
        self.db_session.commit()
        return deleted_count
