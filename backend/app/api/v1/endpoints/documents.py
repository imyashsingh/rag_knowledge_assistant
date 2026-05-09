import os
import tempfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.ingestion.processor import DocumentProcessor
from app.services.document_service import process_document_upload
from app.schemas.document import DocumentResponse
from app.api.deps import get_current_user, get_current_workspace_id, get_current_user_id
from app.db.repositories.document_repo import DocumentRepository
from app.db.session import get_db

router = APIRouter()

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md', '.markdown']


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    current_user: dict = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "UNSUPPORTED_FILE_TYPE",
                    "message": f"Unsupported file type '{file_ext}'. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}",
                    "field": "file",
                    "supported_types": SUPPORTED_EXTENSIONS
                }
            )

        # Validate file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        max_size = 10 * 1024 * 1024  # 10MB

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "FILE_TOO_LARGE",
                    "message": f"File too large. Maximum size is {max_size / (1024 * 1024)}MB",
                    "field": "file",
                    "current_size": file_size,
                    "max_size": max_size
                }
            )

        # Reset file pointer
        await file.seek(0)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Use title from request or generate a user-friendly title from filename
            if title:
                document_title = title
            else:
                # Generate a more user-friendly title from filename
                filename_stem = Path(file.filename).stem
                # Remove file extension and common prefixes
                document_title = filename_stem.replace(
                    '_', ' ').replace('-', ' ').title()

            # Process document
            processor = DocumentProcessor()
            document_id = processor.process_document(
                file_path=temp_file_path,
                title=document_title,
                workspace_id=workspace_id
            )

            if not document_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "DOCUMENT_PROCESSING_FAILED",
                        "message": "Failed to process document",
                        "details": "Document processing service returned no document ID"
                    }
                )

            # Get document details
            doc_repo = DocumentRepository(db)
            document = doc_repo.get_by_id(document_id)

            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "DOCUMENT_NOT_FOUND",
                        "message": "Document not found after processing",
                        "details": "The document was processed but could not be retrieved from the database"
                    }
                )

            return DocumentResponse(
                id=document.id,
                title=document.title,
                filename=document.filename,
                content_type=document.content_type,
                workspace_id=document.workspace_id,
                created_at=document.created_at,
                updated_at=document.updated_at
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DOCUMENT_UPLOAD_FAILED",
                "message": "Document upload failed",
                "details": str(e)
            }
        )


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 50,
    workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """List all documents in the workspace"""
    try:
        doc_repo = DocumentRepository(db)
        documents = doc_repo.get_by_workspace(workspace_id)

        # Apply pagination
        documents = documents[skip:skip + limit]

        return [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                filename=doc.filename,
                content_type=doc.content_type,
                workspace_id=doc.workspace_id,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DOCUMENT_LIST_FAILED",
                "message": "Failed to list documents",
                "details": str(e)
            }
        )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Get document by ID"""
    try:
        doc_repo = DocumentRepository(db)
        document = doc_repo.get_with_chunks(document_id, workspace_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        return DocumentResponse(
            id=document.id,
            title=document.title,
            filename=document.filename,
            content_type=document.content_type,
            workspace_id=document.workspace_id,
            created_at=document.created_at,
            updated_at=document.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DOCUMENT_RETRIEVAL_FAILED",
                "message": "Failed to get document",
                "details": str(e)
            }
        )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Delete a document and its chunks"""
    try:
        doc_repo = DocumentRepository(db)

        # Check if document exists and belongs to workspace
        document = doc_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "DOCUMENT_NOT_FOUND",
                    "message": f"Document with ID {document_id} not found",
                    "field": "document_id"
                }
            )
        elif document.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "DOCUMENT_ACCESS_DENIED",
                    "message": "You don't have permission to access this document",
                    "field": "workspace_id"
                }
            )

        # Delete document (chunks will be deleted via cascade)
        success = doc_repo.delete(document_id)

        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "DOCUMENT_DELETE_FAILED",
                    "message": "Failed to delete document",
                    "details": "Database operation failed"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
