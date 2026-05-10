from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SourceDocument(BaseModel):
    document_id: int
    document_title: str
    chunk_text: str
    relevance_score: Optional[float] = None


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    query: str
    max_sources: Optional[int] = 5
    session_id: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    query: str
    confidence: Optional[float] = None
    is_grounded: Optional[bool] = None
    external_knowledge_detected: Optional[bool] = None
    quality_assured: Optional[bool] = None
    generation_attempts: Optional[int] = None
    retrieval_method: Optional[str] = None
    context_count: Optional[int] = None
