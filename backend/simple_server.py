#!/usr/bin/env python3
"""
Simplified FastAPI server for testing API endpoints without ML dependencies
"""

from fastapi import Header, UploadFile, File, Form
import os
import sys
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uvicorn

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock data and models for testing


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    workspace_id: int
    created_at: datetime


class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    content_type: str
    workspace_id: int
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    query: str
    max_sources: int = 5


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str
    response_time: float


# Create FastAPI app
app = FastAPI(
    title="DocuMind API (Test Mode)",
    description="Simplified API for testing endpoints",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
users_db = {}
documents_db = {}
tokens_db = {}
user_id_counter = 1
doc_id_counter = 1

# Helper functions


def generate_token():
    return f"mock_token_{datetime.now().timestamp()}"


def verify_token(token: str):
    if token in tokens_db:
        return tokens_db[token]
    raise HTTPException(status_code=401, detail="Invalid token")

# Root endpoint


@app.get("/")
async def root():
    return {
        "message": "DocuMind API (Test Mode)",
        "version": "1.0.0-test",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Health endpoints


@app.get("/api/v1/health/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-test",
        "components": {
            "database": {"status": "healthy", "message": "Mock database connection successful"},
            "redis": {"status": "healthy", "message": "Mock Redis connection successful"},
            "groq": {"status": "healthy", "message": "Mock Groq API connection successful"},
            "document_processor": {"status": "healthy", "message": "Mock document processor ready"}
        }
    }


@app.get("/api/v1/health/simple")
async def simple_health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/health/ready")
async def readiness_check():
    return {"status": "ready"}


@app.get("/api/v1/health/live")
async def liveness_check():
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

# Authentication endpoints


@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    global user_id_counter

    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create user
    user = {
        "id": user_id_counter,
        "email": user_data.email,
        "password": user_data.password,  # In real app, this would be hashed
        "workspace_id": 1,
        "created_at": datetime.utcnow()
    }
    users_db[user_data.email] = user
    user_id_counter += 1

    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()
    tokens_db[access_token] = user

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    if user_data.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = users_db[user_data.email]
    if user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()
    tokens_db[access_token] = user

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(token_data: dict):
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    # In real app, validate refresh token
    access_token = generate_token()
    new_refresh_token = generate_token()

    # Get user from existing token (simplified)
    user = {"id": 1, "email": "test@example.com", "workspace_id": 1}
    tokens_db[access_token] = user

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@app.post("/api/v1/auth/logout")
async def logout(authorization: str = None):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if token in tokens_db:
            del tokens_db[token]

    return {"message": "Successfully logged out"}


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    return UserResponse(
        id=user["id"],
        email=user["email"],
        workspace_id=user["workspace_id"],
        created_at=user["created_at"]
    )

# Document endpoints


@app.post("/api/v1/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    authorization: str = Header(None, alias="Authorization")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    global doc_id_counter

    # Mock document creation
    doc = {
        "id": doc_id_counter,
        "title": title or "Test Document",
        "filename": "test.txt",
        "content_type": "text/plain",
        "workspace_id": user["workspace_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    documents_db[doc_id_counter] = doc
    doc_id_counter += 1

    return DocumentResponse(**doc)


@app.get("/api/v1/documents/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(None, alias="Authorization")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    # Get user's documents
    user_docs = [
        doc for doc in documents_db.values()
        if doc["workspace_id"] == user["workspace_id"]
    ]

    # Apply pagination
    paginated_docs = user_docs[skip:skip + limit]

    return [DocumentResponse(**doc) for doc in paginated_docs]


@app.get("/api/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    authorization: str = Header(None, alias="Authorization")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = documents_db[document_id]
    if doc["workspace_id"] != user["workspace_id"]:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(**doc)


@app.delete("/api/v1/documents/{document_id}")
async def delete_document(
    document_id: int,
    authorization: str = Header(None, alias="Authorization")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = documents_db[document_id]
    if doc["workspace_id"] != user["workspace_id"]:
        raise HTTPException(status_code=404, detail="Document not found")

    del documents_db[document_id]
    return {"message": "Document deleted successfully"}

# Chat endpoints


@app.post("/api/v1/chat/query", response_model=ChatResponse)
async def chat_query(
    chat_request: ChatRequest,
    authorization: str = Header(None, alias="Authorization")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    # Mock RAG response
    response = ChatResponse(
        answer=f"This is a mock response to your query: '{chat_request.query}'. In a real implementation, this would use RAG to provide an answer based on your documents.",
        sources=[{"title": "Mock Source 1", "content": "Mock content"}],
        query=chat_request.query,
        response_time=0.5
    )

    return response


@app.get("/api/v1/chat/stats")
async def get_chat_workspace_stats(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    return {
        "total_documents": len(documents_db),
        "total_chunks": 10,
        "workspace_id": user["workspace_id"],
        "last_updated": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/chat/clear-cache")
async def clear_chat_cache(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = verify_token(token)

    return {"message": "Cache cleared successfully"}


@app.post("/api/v1/chat/legacy")
async def legacy_query(q: str, ws: str):
    """Legacy endpoint for backward compatibility"""
    response = {
        "answer": f"Legacy response to: '{q}' in workspace {ws}",
        "sources": []
    }
    return response

if __name__ == "__main__":
    print("🚀 Starting simplified DocuMind API server for testing...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/health/")
    print("⚠️  This is a test server with mock data and no ML dependencies")

    uvicorn.run(app, host="0.0.0.0", port=8000)
