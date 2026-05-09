"""
Enhanced Retrieval System for Enterprise RAG
Implements hybrid search with vector + keyword matching
"""

import math
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.rag.embeddings import generate_embedding
from app.db.models.chunk import Chunk
from app.db.models.document import Document


class HybridRetriever:
    """Hybrid retrieval system combining vector and keyword search"""
    
    def __init__(self):
        self.vector_weight = 0.6
        self.keyword_weight = 0.4
        self.min_relevance_score = 0.3
    
    def calculate_bm25_score(self, query: str, document: str, k: float = 1.2, b: float = 0.75) -> float:
        """
        Calculate BM25 score for keyword relevance
        Simple implementation - can be enhanced with proper BM25
        """
        query_terms = query.lower().split()
        doc_terms = document.lower().split()
        
        if not query_terms or not doc_terms:
            return 0.0
        
        doc_length = len(doc_terms)
        avg_doc_length = 100  # Simplified - should be calculated from corpus
        
        bm25_score = 0.0
        for term in query_terms:
            if term in doc_terms:
                # Simplified BM25 calculation
                tf = doc_terms.count(term)
                idf = math.log(1 + 1 / 1)  # Simplified IDF
                
                score = (idf * tf * (k + 1)) / (tf + k * (1 - b + b * (doc_length / avg_doc_length)))
                bm25_score += score
        
        return bm25_score
    
    def hybrid_search(
        self,
        query: str,
        workspace_id: int,
        db: Session,
        limit: int = 10,
        use_reranking: bool = True
    ) -> List[Tuple[str, int, str, float, Dict[str, float]]]:
        """
        Hybrid search combining vector similarity and keyword matching
        
        Returns:
            List of tuples: (chunk_text, document_id, document_title, combined_score, scores_dict)
        """
        try:
            # 1. Vector Search
            vector_results = self._vector_search(query, workspace_id, db, limit * 2)
            
            # 2. Keyword Search
            keyword_results = self._keyword_search(query, workspace_id, db, limit * 2)
            
            # 3. Combine Results
            combined_results = self._combine_search_results(vector_results, keyword_results)
            
            # 4. Answer Relevance Filtering
            filtered_results = self._filter_for_answer_relevance(query, combined_results)
            
            # 5. Reranking
            if use_reranking and len(filtered_results) > 1:
                filtered_results = self._rerank_results(query, filtered_results)
            
            # 6. Return top results
            return filtered_results[:limit]
            
        except Exception as e:
            raise Exception(f"Hybrid search failed: {str(e)}")
    
    def _vector_search(
        self,
        query: str,
        workspace_id: int,
        db: Session,
        limit: int
    ) -> List[Tuple[str, int, str, float]]:
        """Vector similarity search"""
        query_embedding = generate_embedding(query)
        embedding_str = str(query_embedding)
        
        results = db.execute(text("""
            SELECT 
                c.text,
                c.document_id,
                d.title as document_title,
                1 - (c.embedding <=> :query_embedding) as similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.workspace_id = :workspace_id
            ORDER BY c.embedding <=> :query_embedding
            LIMIT :limit
        """), {
            "query_embedding": embedding_str,
            "workspace_id": workspace_id,
            "limit": limit
        }).fetchall()
        
        vector_results = []
        for row in results:
            chunk_text, document_id, document_title, similarity = row
            vector_results.append((chunk_text, document_id, document_title, float(similarity)))
        
        return vector_results
    
    def _keyword_search(
        self,
        query: str,
        workspace_id: int,
        db: Session,
        limit: int
    ) -> List[Tuple[str, int, str, float]]:
        """Keyword-based search using BM25"""
        results = db.execute(text("""
            SELECT 
                c.text,
                c.document_id,
                d.title as document_title
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.workspace_id = :workspace_id
            LIMIT :limit
        """), {
            "workspace_id": workspace_id,
            "limit": limit
        }).fetchall()
        
        keyword_results = []
        for row in results:
            chunk_text, document_id, document_title = row
            
            # Calculate BM25 score
            bm25_score = self.calculate_bm25_score(query, chunk_text)
            keyword_results.append((chunk_text, document_id, document_title, bm25_score))
        
        # Sort by BM25 score
        keyword_results.sort(key=lambda x: x[3], reverse=True)
        
        return keyword_results
    
    def _combine_search_results(
        self,
        vector_results: List[Tuple[str, int, str, float]],
        keyword_results: List[Tuple[str, int, str, float]]
    ) -> List[Tuple[str, int, str, float, Dict[str, float]]]:
        """Combine vector and keyword search results"""
        combined = {}
        
        # Add vector results
        for chunk_text, doc_id, doc_title, vector_score in vector_results:
            key = f"{doc_id}:{hash(chunk_text)}"
            combined[key] = {
                'chunk_text': chunk_text,
                'document_id': doc_id,
                'document_title': doc_title,
                'vector_score': vector_score,
                'keyword_score': 0.0
            }
        
        # Add keyword results and merge
        for chunk_text, doc_id, doc_title, keyword_score in keyword_results:
            key = f"{doc_id}:{hash(chunk_text)}"
            if key in combined:
                combined[key]['keyword_score'] = keyword_score
            else:
                combined[key] = {
                    'chunk_text': chunk_text,
                    'document_id': doc_id,
                    'document_title': doc_title,
                    'vector_score': 0.0,
                    'keyword_score': keyword_score
                }
        
        # Calculate combined scores
        final_results = []
        for key, data in combined.items():
            vector_score = data['vector_score']
            keyword_score = data['keyword_score']
            
            # Normalize scores (simplified)
            normalized_vector = min(vector_score, 1.0)
            normalized_keyword = min(keyword_score / 10.0, 1.0)  # BM25 scores can be >1
            
            combined_score = (
                self.vector_weight * normalized_vector + 
                self.keyword_weight * normalized_keyword
            )
            
            if combined_score >= self.min_relevance_score:
                final_results.append((
                    data['chunk_text'],
                    data['document_id'],
                    data['document_title'],
                    combined_score,
                    {
                        'vector_score': vector_score,
                        'keyword_score': keyword_score,
                        'normalized_vector': normalized_vector,
                        'normalized_keyword': normalized_keyword
                    }
                ))
        
        # Sort by combined score
        final_results.sort(key=lambda x: x[3], reverse=True)
        
        return final_results
    
    def _filter_for_answer_relevance(
        self,
        query: str,
        results: List[Tuple[str, int, str, float, Dict[str, float]]]
    ) -> List[Tuple[str, int, str, float, Dict[str, float]]]:
        """Filter results for answer relevance"""
        relevant_results = []
        query_words = set(query.lower().split())
        
        for chunk_text, doc_id, doc_title, combined_score, scores in results:
            chunk_words = set(chunk_text.lower().split())
            
            # Check for answer relevance indicators
            word_overlap = len(query_words & chunk_words) / len(query_words | chunk_words)
            
            # Keep if has reasonable word overlap or high similarity
            if word_overlap >= 0.1 or combined_score >= 0.5:
                relevant_results.append((chunk_text, doc_id, doc_title, combined_score, scores))
        
        return relevant_results
    
    def _rerank_results(
        self,
        query: str,
        results: List[Tuple[str, int, str, float, Dict[str, float]]]
    ) -> List[Tuple[str, int, str, float, Dict[str, float]]]:
        """Enhanced reranking with multiple factors"""
        query_words = set(query.lower().split())
        
        reranked = []
        for chunk_text, doc_id, doc_title, combined_score, scores in results:
            chunk_words = set(chunk_text.lower().split())
            
            # Multiple reranking factors
            word_overlap = len(query_words & chunk_words) / len(query_words | chunk_words)
            
            # Answer presence indicators
            answer_indicators = ['answer', 'result', 'solution', 'because', 'therefore', 'thus']
            has_answer_indicators = any(indicator in chunk_text.lower() for indicator in answer_indicators)
            
            # Length penalty (prefer concise, relevant chunks)
            length_penalty = min(len(chunk_text) / 1000, 1.0)
            
            # Final reranking score
            rerank_score = (
                0.5 * combined_score +
                0.2 * word_overlap +
                0.2 * (1.0 - length_penalty) +
                0.1 * (1.0 if has_answer_indicators else 0.0)
            )
            
            reranked.append((chunk_text, doc_id, doc_title, rerank_score, scores))
        
        # Sort by rerank score
        reranked.sort(key=lambda x: x[3], reverse=True)
        
        return reranked


def search_similar_chunks_v2(
    query: str,
    workspace_id: int,
    db: Session,
    limit: int = 5,
    rerank: bool = True
) -> List[Tuple[str, int, str, float, Dict[str, float]]]:
    """
    Enhanced search using hybrid retrieval
    
    Returns:
        List of tuples: (chunk_text, document_id, document_title, score, detailed_scores)
    """
    retriever = HybridRetriever()
    return retriever.hybrid_search(query, workspace_id, db, limit, rerank)
