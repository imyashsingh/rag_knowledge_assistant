from pydantic import BaseModel
from typing import List, Optional


class SourceDocument(BaseModel):
    document_id: int
    document_title: str
    chunk_text: str
    relevance_score: Optional[float] = None


class ChatRequest(BaseModel):
    query: str
    max_sources: Optional[int] = 5


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    query: str
