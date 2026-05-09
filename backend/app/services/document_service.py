from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.ingestion.processor import DocumentProcessor
from app.db.repositories.document_repo import DocumentRepository
from app.core.exceptions import DocumentProcessingException


def process_document_upload(
    file_path: str,
    title: str,
    workspace_id: int,
    db: Session,
    use_semantic_chunking: bool = False
) -> Optional[int]:
    """
    Process document upload and return document ID

    Args:
        file_path: Path to the uploaded file
        title: Document title
        workspace_id: Workspace ID for isolation
        use_semantic_chunking: Whether to use semantic chunking

    Returns:
        Document ID if successful, None otherwise
    """
    try:
        processor = DocumentProcessor(
            use_semantic_chunking=use_semantic_chunking)

        # Process document
        document_id = processor.process_document(
            file_path, title, workspace_id)

        # Clear workspace cache to invalidate stale answers
        if document_id:
            from app.rag.orchestrator import clear_rag_cache
            clear_rag_cache(workspace_id)

        return document_id
    except Exception as e:
        raise DocumentProcessingException(
            f"Document processing failed: {str(e)}")


def get_document_stats(document_id: int, workspace_id: int, db: Session) -> Dict[str, Any]:
    """Get statistics for a specific document"""
    try:
        doc_repo = DocumentRepository(db)
        document = doc_repo.get_with_chunks(document_id, workspace_id)

        if not document:
            return {"error": "Document not found"}

        chunk_count = len(document.chunks) if document.chunks else 0

        return {
            "document_id": document.id,
            "title": document.title,
            "filename": document.filename,
            "content_type": document.content_type,
            "chunk_count": chunk_count,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
    except Exception as e:
        raise DocumentProcessingException(
            f"Failed to get document stats: {str(e)}")


def list_workspace_documents(workspace_id: int, db: Session, skip: int = 0, limit: int = 50) -> Dict[str, Any]:
    """List documents in workspace with pagination"""
    try:
        doc_repo = DocumentRepository(db)
        documents = doc_repo.get_by_workspace(workspace_id)

        # Apply pagination
        total = len(documents)
        documents = documents[skip:skip + limit]

        return {
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "filename": doc.filename,
                    "content_type": doc.content_type,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
                }
                for doc in documents
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise DocumentProcessingException(
            f"Failed to list documents: {str(e)}")


def delete_document_service(document_id: int, workspace_id: int, db: Session) -> bool:
    """Delete document and all associated chunks"""
    try:
        doc_repo = DocumentRepository(db)

        # Verify document exists and belongs to workspace
        document = doc_repo.get_by_id(document_id)
        if not document or document.workspace_id != workspace_id:
            return False

        # Delete document
        success = doc_repo.delete(document_id)

        # Clear workspace cache to invalidate stale answers
        if success:
            from app.rag.orchestrator import clear_rag_cache
            clear_rag_cache(workspace_id)

        return success
    except Exception as e:
        raise DocumentProcessingException(
            f"Failed to delete document: {str(e)}")


# Legacy function for backward compatibility
def process_file(text: str, db: Session, workspace_id: str = "ws1"):
    """Legacy function - use process_document_upload instead"""
    try:
        # This is a simplified legacy function
        # In production, use the full document processing pipeline
        from app.rag.embeddings import generate_embedding
        from app.db.repositories.chunk_repo import ChunkRepository

        # Create a simple document and chunk
        doc_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)

        # Create document (simplified)
        document = doc_repo.create_document(
            title="Legacy Document",
            filename="legacy.txt",
            content_type="text/plain",
            workspace_id=int(workspace_id.replace("ws", ""))
        )

        # Create chunk with embedding
        embedding = generate_embedding(text)
        chunk_repo.create_chunk(
            text=text,
            embedding=embedding,
            workspace_id=int(workspace_id.replace("ws", "")),
            document_id=document.id,
            chunk_index=0
        )

        return document.id
    except Exception as e:
        raise DocumentProcessingException(
            f"Legacy processing failed: {str(e)}")
