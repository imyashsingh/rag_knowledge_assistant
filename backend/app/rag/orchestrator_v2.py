"""
Enterprise RAG Orchestrator V2
Industry-standard RAG with strict context enforcement and quality control
"""

from typing import Dict, Any, Optional
import hashlib
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.rag.retriever_v2 import search_similar_chunks_v2
from app.rag.generator import generate_chat_response_enterprise
from app.core.redis_client import redis_client
from app.schemas.chat import ChatResponse, SourceDocument
from app.db.repositories.document_repo import DocumentRepository


def run_enterprise_rag_pipeline(
    query: str,
    workspace_id: int,
    user_id: int,
    max_sources: int = 5,
    db: Session = None
) -> Optional[ChatResponse]:
    """
    Enterprise-grade RAG pipeline with strict context enforcement
    
    Args:
        query: User's question
        workspace_id: Workspace ID for isolation
        user_id: User ID for tracking
        max_sources: Maximum number of sources to retrieve
        db: Database session (optional, will create if not provided)

    Returns:
        ChatResponse with answer, sources, and quality metrics
    """
    try:
        # Get workspace document count for cache versioning
        db_session = db or SessionLocal()
        should_close_db = db is None

        try:
            doc_repo = DocumentRepository(db_session)
            doc_count = len(doc_repo.get_by_workspace(workspace_id))
        finally:
            if should_close_db:
                db_session.close()

        # Track query frequency for smart caching
        track_query_frequency(workspace_id, query)

        # Check cache first with workspace versioning
        cache_key = f"enterprise_rag:{workspace_id}:{doc_count}:{hashlib.md5(query.encode()).hexdigest()}"
        cached_response = redis_client.get(cache_key)
        if cached_response:
            cached_data = json.loads(cached_response)
            return ChatResponse(**cached_data)

        # Use provided db session or create temporary one
        if db is None:
            db = SessionLocal()
            should_close_db = True
        else:
            should_close_db = False

        try:
            # Step 1: Enhanced Retrieval with Hybrid Search
            search_results = search_similar_chunks_v2(
                query=query,
                workspace_id=workspace_id,
                db=db,
                limit=max_sources,
                rerank=True
            )

            if not search_results:
                return ChatResponse(
                    answer="I don't have enough information to answer this question based on the provided documents.",
                    sources=[],
                    query=query,
                    confidence=1.0,
                    is_grounded=True,
                    external_knowledge_detected=False,
                    quality_assured=True
                )

            # Step 2: Extract context chunks and source information
            context_chunks = []
            sources = []

            for chunk_text, document_id, document_title, combined_score, detailed_scores in search_results:
                context_chunks.append(chunk_text)
                sources.append(SourceDocument(
                    document_id=document_id,
                    document_title=document_title,
                    chunk_text=chunk_text,
                    relevance_score=combined_score,
                    detailed_scores=detailed_scores
                ))

            # Step 3: Context-Only Generation with Grounding Verification
            generation_result = generate_chat_response_enterprise(query, context_chunks)
            
            answer = generation_result['answer']
            confidence = generation_result['confidence']
            grounding_analysis = generation_result.get('grounding_analysis')
            is_grounded = generation_result['is_grounded']
            external_knowledge_detected = generation_result['external_knowledge_detected']
            attempts = generation_result['attempts']

            # Step 4: Quality Control Check
            quality_assured = (
                is_grounded and 
                confidence >= 0.7 and 
                not external_knowledge_detected
            )

            # Step 5: Build Response with Quality Metrics
            response = ChatResponse(
                answer=answer,
                sources=sources,
                query=query,
                confidence=confidence,
                is_grounded=is_grounded,
                external_knowledge_detected=external_knowledge_detected,
                quality_assured=quality_assured,
                generation_attempts=attempts,
                retrieval_method="hybrid_vector_keyword",
                context_count=len(context_chunks)
            )

            # Step 6: Cache only high-quality responses
            if quality_assured:
                cache_size = get_workspace_cache_size(workspace_id)
                query_freq = get_query_frequency(workspace_id, query)
                
                # Only cache frequently asked questions or if under size limit
                if cache_size < 1000 or query_freq > 1:
                    redis_client.set(cache_key, response.model_dump_json(), ex=300)
                    increment_workspace_cache_count(workspace_id)

            return response

        finally:
            # Close database session if we created it
            if should_close_db:
                db.close()

    except Exception as e:
        print(f"Error in Enterprise RAG pipeline: {str(e)}")
        return ChatResponse(
            answer="I encountered an error while processing your question. Please try again.",
            sources=[],
            query=query,
            confidence=0.0,
            is_grounded=False,
            external_knowledge_detected=False,
            quality_assured=False,
            error=str(e)
        )


def get_workspace_stats(workspace_id: int, db: Session) -> Dict[str, Any]:
    """Get statistics about workspace documents and chunks"""
    try:
        doc_count = get_workspace_document_count(workspace_id, db)

        return {
            "document_count": doc_count,
            "workspace_id": workspace_id,
            "rag_version": "enterprise_v2",
            "features": [
                "hybrid_retrieval",
                "grounding_verification",
                "confidence_scoring",
                "quality_control"
            ]
        }
    except Exception as e:
        print(f"Error getting workspace stats: {str(e)}")
        return {"document_count": 0, "workspace_id": workspace_id}


def clear_enterprise_rag_cache(workspace_id: Optional[int] = None) -> bool:
    """Clear Enterprise RAG cache for workspace or all"""
    try:
        if workspace_id:
            # Clear specific workspace cache
            pattern = f"enterprise_rag:{workspace_id}:*"
            # Reset workspace cache count
            redis_client.delete(f"cache_count:workspace:{workspace_id}")
        else:
            # Clear all Enterprise RAG cache
            pattern = "enterprise_rag:*"

        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Error clearing Enterprise RAG cache: {str(e)}")
        return False


def get_workspace_cache_size(workspace_id: int) -> int:
    """Get current cache size for workspace"""
    try:
        count = redis_client.get(f"cache_count:workspace:{workspace_id}")
        return int(count) if count else 0
    except:
        return 0


def increment_workspace_cache_count(workspace_id: int):
    """Increment workspace cache count"""
    try:
        redis_client.incr(f"cache_count:workspace:{workspace_id}")
        redis_client.expire(f"cache_count:workspace:{workspace_id}", 86400)  # 24 hours
    except:
        pass


def track_query_frequency(workspace_id: int, query: str):
    """Track how often queries are asked"""
    try:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"query_freq:{workspace_id}:{query_hash}"
        redis_client.incr(key)
        redis_client.expire(key, 86400)  # Track for 24 hours
    except:
        pass


def get_query_frequency(workspace_id: int, query: str) -> int:
    """Get how many times a query was asked"""
    try:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"query_freq:{workspace_id}:{query_hash}"
        freq = redis_client.get(key)
        return int(freq) if freq else 0
    except:
        return 0


def get_workspace_document_count(workspace_id: int, db: Session) -> int:
    """Get count of documents in workspace"""
    try:
        from app.db.models.document import Document
        return db.query(Document).filter(Document.workspace_id == workspace_id).count()
    except:
        return 0


def validate_rag_quality(response: ChatResponse) -> Dict[str, Any]:
    """
    Validate RAG response quality
    
    Returns:
        Dict with quality assessment and recommendations
    """
    quality_score = 0.0
    issues = []
    recommendations = []

    # Check grounding
    if response.is_grounded:
        quality_score += 0.4
    else:
        issues.append("Answer not properly grounded in context")
        recommendations.append("Regenerate with stricter context enforcement")

    # Check confidence
    if response.confidence >= 0.8:
        quality_score += 0.3
    elif response.confidence >= 0.6:
        quality_score += 0.2
    else:
        issues.append("Low confidence score")
        recommendations.append("Improve retrieval or context quality")

    # Check external knowledge
    if not response.external_knowledge_detected:
        quality_score += 0.2
    else:
        issues.append("External knowledge detected")
        recommendations.append("Enhance grounding verification")

    # Check sources
    if response.sources and len(response.sources) > 0:
        quality_score += 0.1
    else:
        issues.append("No sources provided")
        recommendations.append("Improve document retrieval")

    return {
        "quality_score": quality_score,
        "quality_grade": "A" if quality_score >= 0.9 else "B" if quality_score >= 0.7 else "C" if quality_score >= 0.5 else "D",
        "is_high_quality": quality_score >= 0.7,
        "issues": issues,
        "recommendations": recommendations,
        "metrics": {
            "grounding": response.is_grounded,
            "confidence": response.confidence,
            "no_external_knowledge": not response.external_knowledge_detected,
            "has_sources": len(response.sources) > 0
        }
    }
