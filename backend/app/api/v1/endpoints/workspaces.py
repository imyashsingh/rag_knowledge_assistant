from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate, WorkspaceWithUsers, WorkspaceStats
from app.api.deps import get_current_user, get_current_workspace_id, get_current_user_id
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.chat_history_repo import ChatHistoryRepository
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new workspace"""
    try:
        workspace_repo = WorkspaceRepository(db)

        # Check if workspace name already exists for this user
        existing_workspace = workspace_repo.get_by_name(workspace_data.name)
        if existing_workspace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace with this name already exists"
            )

        # Create workspace
        workspace = workspace_repo.create_workspace(workspace_data.name)

        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            created_at=workspace.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace: {str(e)}"
        )


@router.get("/", response_model=list[WorkspaceResponse])
def list_user_workspaces(
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all workspaces for the current user"""
    try:
        workspace_repo = WorkspaceRepository(db)
        user_repo = UserRepository(db)

        # Get user's workspaces
        user = user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # For now, return the user's current workspace
        # In a full implementation, you'd have a user_workspaces join table
        current_workspace = workspace_repo.get_by_id(user.workspace_id)
        if current_workspace:
            return [WorkspaceResponse(
                id=current_workspace.id,
                name=current_workspace.name,
                created_at=current_workspace.created_at
            )]
        else:
            return []

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workspaces: {str(e)}"
        )


@router.get("/{workspace_id}", response_model=WorkspaceWithUsers)
def get_workspace(
    workspace_id: int,
    current_user: dict = Depends(get_current_user),
    user_workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Get workspace details with users"""
    try:
        # Ensure user can only access their own workspace
        if workspace_id != user_workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )

        workspace_repo = WorkspaceRepository(db)
        workspace = workspace_repo.get_with_users(workspace_id)

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Get user information
        users = []
        if workspace.users:
            users = [
                {
                    "id": user.id,
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                }
                for user in workspace.users
            ]

        return WorkspaceWithUsers(
            id=workspace.id,
            name=workspace.name,
            created_at=workspace.created_at,
            users=users
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace: {str(e)}"
        )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    current_user: dict = Depends(get_current_user),
    user_workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Update workspace details"""
    try:
        # Ensure user can only update their own workspace
        if workspace_id != user_workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )

        workspace_repo = WorkspaceRepository(db)

        if not workspace_data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name is required for update"
            )

        # Check if new name conflicts with existing workspace
        existing_workspace = workspace_repo.get_by_name(workspace_data.name)
        if existing_workspace and existing_workspace.id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace with this name already exists"
            )

        workspace = workspace_repo.update(
            workspace_id, name=workspace_data.name)

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            created_at=workspace.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workspace: {str(e)}"
        )


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    current_user: dict = Depends(get_current_user),
    user_workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Delete a workspace (cascade deletes documents, chunks, and chat history)"""
    try:
        # Prevent deletion of current workspace
        if workspace_id == user_workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your current workspace"
            )

        workspace_repo = WorkspaceRepository(db)

        # Check if workspace exists
        workspace = workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Delete workspace (cascade will handle related data)
        success = workspace_repo.delete(workspace_id)

        if success:
            return {"message": "Workspace deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete workspace"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workspace: {str(e)}"
        )


@router.get("/{workspace_id}/stats", response_model=WorkspaceStats)
def get_workspace_statistics(
    workspace_id: int,
    current_user: dict = Depends(get_current_user),
    user_workspace_id: int = Depends(get_current_workspace_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive workspace statistics"""
    try:
        # Ensure user can only access their own workspace stats
        if workspace_id != user_workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )

        workspace_repo = WorkspaceRepository(db)
        doc_repo = DocumentRepository(db)
        user_repo = UserRepository(db)
        chat_repo = ChatHistoryRepository(db)

        # Get workspace
        workspace = workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Get statistics
        document_count = len(doc_repo.get_workspace_documents(workspace_id))
        user_count = len(user_repo.get_workspace_users(workspace_id))
        chat_stats = chat_repo.get_chat_statistics(workspace_id)
        chat_count = chat_stats.get("total_chats", 0)

        return WorkspaceStats(
            id=workspace.id,
            name=workspace.name,
            document_count=document_count,
            user_count=user_count,
            chat_count=chat_count,
            created_at=workspace.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace statistics: {str(e)}"
        )
