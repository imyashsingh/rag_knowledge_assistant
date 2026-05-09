"""
Context-Only Generation System for Enterprise RAG
Strict enforcement of context-only responses with quality control
"""

from typing import Optional, Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.rag.grounding import AnswerGrounding

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


class ContextOnlyGenerator:
    """Context-only LLM generator with strict grounding enforcement"""
    
    def __init__(self):
        self.grounding_verifier = AnswerGrounding()
        self.max_attempts = 3
        self.temperature = 0.1  # Low temperature for consistency
        self.max_tokens = 500
    
    def build_strict_context_prompt(self, query: str, context_chunks: List[str]) -> str:
        """Build strict context-only prompt"""
        context = "\n\n".join(
            [f"CONTEXT DOCUMENT {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)]
        )
        
        prompt = f"""You are a DOCUMENT-BASED QUESTION ANSWERING SYSTEM. You can ONLY use the provided context documents.

{context}

QUESTION: {query}

STRICT RULES:
1. You MUST answer using ONLY the context documents above
2. If the context documents do NOT contain the answer, you MUST respond exactly with: "I don't have enough information to answer this question based on the provided documents."
3. Do NOT use any external knowledge, training data, or general information
4. Do NOT make up, infer, or assume information not present in the context
5. Cite the document number when using information (e.g., "According to CONTEXT DOCUMENT 1...")
6. Be concise and factual

ANSWER:"""
        
        return prompt
    
    def generate_with_grounding_check(
        self,
        query: str,
        context_chunks: List[str],
        model: str = "llama-3.1-8b-instant"
    ) -> Dict[str, Any]:
        """
        Generate answer with automatic grounding verification
        
        Returns:
            Dict with answer, confidence, grounding_analysis, etc.
        """
        if not context_chunks:
            return {
                'answer': "I don't have enough information to answer this question based on the provided documents.",
                'confidence': 1.0,
                'grounding_analysis': None,
                'attempts': 0,
                'is_grounded': True,
                'external_knowledge_detected': False
            }
        
        context = "\n\n".join(context_chunks)
        
        for attempt in range(self.max_attempts):
            try:
                # Generate answer
                prompt = self.build_strict_context_prompt(query, context_chunks)
                answer = self._generate_llm_response(prompt, model)
                
                # Verify grounding
                grounding_report = self.grounding_verifier.generate_grounding_report(answer, context)
                
                # Check if answer is properly grounded
                if grounding_report['is_grounded']:
                    return {
                        'answer': answer,
                        'confidence': self._calculate_confidence(grounding_report),
                        'grounding_analysis': grounding_report,
                        'attempts': attempt + 1,
                        'is_grounded': True,
                        'external_knowledge_detected': False
                    }
                elif attempt == self.max_attempts - 1:
                    # Last attempt - return fallback
                    return {
                        'answer': "I don't have enough information to answer this question based on the provided documents.",
                        'confidence': 1.0,
                        'grounding_analysis': grounding_report,
                        'attempts': attempt + 1,
                        'is_grounded': False,
                        'external_knowledge_detected': True
                    }
                else:
                    # Try again with stricter prompt
                    continue
                    
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    return {
                        'answer': "I encountered an error while generating a response. Please try again.",
                        'confidence': 0.0,
                        'grounding_analysis': None,
                        'attempts': attempt + 1,
                        'is_grounded': False,
                        'external_knowledge_detected': False,
                        'error': str(e)
                    }
                continue
        
        return {
            'answer': "I don't have enough information to answer this question based on the provided documents.",
            'confidence': 1.0,
            'grounding_analysis': None,
            'attempts': self.max_attempts,
            'is_grounded': True,
            'external_knowledge_detected': False
        }
    
    def _generate_llm_response(self, prompt: str, model: str) -> str:
        """Generate response from LLM"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def _calculate_confidence(self, grounding_report: Dict[str, Any]) -> float:
        """Calculate confidence score based on grounding analysis"""
        if not grounding_report:
            return 0.0
        
        analysis = grounding_report.get('grounding_analysis', {})
        grounded_ratio = analysis.get('grounded_ratio', 0.0)
        
        # Base confidence from grounding ratio
        confidence = grounded_ratio
        
        # Boost confidence if no external knowledge detected
        if not grounding_report.get('external_knowledge_detected', False):
            confidence = min(confidence + 0.2, 1.0)
        
        # Penalty for many ungrounded sentences
        ungrounded_count = analysis.get('ungrounded_sentences', 0)
        if ungrounded_count > 0:
            confidence = max(confidence - (ungrounded_count * 0.1), 0.0)
        
        return round(confidence, 2)
    
    def generate_chat_response_v2(
        self,
        query: str,
        context_chunks: List[str],
        model: str = "llama-3.1-8b-instant"
    ) -> Dict[str, Any]:
        """
        Main interface for context-only generation
        
        Returns:
            Dict with answer and metadata
        """
        result = self.generate_with_grounding_check(query, context_chunks, model)
        
        # Add metadata
        result.update({
            'context_count': len(context_chunks),
            'model_used': model,
            'generation_method': 'context_only_with_grounding',
            'quality_assured': result['is_grounded'] and result['confidence'] >= 0.7
        })
        
        return result


def generate_chat_response_enterprise(
    query: str,
    context_chunks: List[str],
    model: str = "llama-3.1-8b-instant"
) -> Dict[str, Any]:
    """
    Enterprise-grade context-only response generation
    
    Returns:
        Dict with answer, confidence, grounding_analysis, and metadata
    """
    generator = ContextOnlyGenerator()
    return generator.generate_chat_response_v2(query, context_chunks, model)
