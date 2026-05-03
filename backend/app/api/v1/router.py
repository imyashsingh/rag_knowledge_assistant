from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, documents, health, workspaces

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(documents.router, prefix="/documents")
api_router.include_router(workspaces.router, prefix="/workspaces")
api_router.include_router(health.router, prefix="/health")
