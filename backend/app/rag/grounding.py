"""
Answer Grounding Verification System for Enterprise RAG
Ensures answers come strictly from provided context
"""

import re
from typing import List, Tuple, Dict, Any
import hashlib


class AnswerGrounding:
    """Verify that LLM answers are grounded in provided context"""
    
    def __init__(self):
        self.similarity_threshold = 0.7  # Minimum similarity for grounding
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be enhanced with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def sentence_similarity(self, sentence: str, context: str) -> float:
        """Calculate similarity between sentence and context"""
        # Simple word overlap similarity - can be enhanced with embeddings
        sentence_words = set(sentence.lower().split())
        context_words = set(context.lower().split())
        
        if not sentence_words:
            return 0.0
        
        intersection = sentence_words & context_words
        union = sentence_words | context_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def verify_sentence_grounding(self, sentence: str, context: str) -> bool:
        """Verify if a sentence is grounded in context"""
        similarity = self.sentence_similarity(sentence, context)
        return similarity >= self.similarity_threshold
    
    def verify_answer_grounding(self, answer: str, context: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify that entire answer is grounded in context
        
        Returns:
            Tuple of (is_grounded, analysis_dict)
        """
        sentences = self.split_into_sentences(answer)
        
        grounded_sentences = []
        ungrounded_sentences = []
        sentence_analyses = []
        
        for i, sentence in enumerate(sentences):
            similarity = self.sentence_similarity(sentence, context)
            is_grounded = similarity >= self.similarity_threshold
            
            analysis = {
                'sentence_index': i,
                'sentence': sentence,
                'similarity': similarity,
                'is_grounded': is_grounded
            }
            
            sentence_analyses.append(analysis)
            
            if is_grounded:
                grounded_sentences.append(sentence)
            else:
                ungrounded_sentences.append(sentence)
        
        # Overall grounding assessment
        total_sentences = len(sentences)
        grounded_ratio = len(grounded_sentences) / total_sentences if total_sentences > 0 else 0
        
        is_fully_grounded = grounded_ratio >= 0.8  # 80% of sentences must be grounded
        
        analysis = {
            'total_sentences': total_sentences,
            'grounded_sentences': len(grounded_sentences),
            'ungrounded_sentences': len(ungrounded_sentences),
            'grounded_ratio': grounded_ratio,
            'is_fully_grounded': is_fully_grounded,
            'sentence_analyses': sentence_analyses,
            'grounded_sentences': grounded_sentences,
            'ungrounded_sentences': ungrounded_sentences
        }
        
        return is_fully_grounded, analysis
    
    def detect_external_knowledge(self, answer: str, context: str) -> List[str]:
        """
        Detect potential external knowledge usage
        Returns list of potentially ungrounded sentences
        """
        sentences = self.split_into_sentences(answer)
        external_sentences = []
        
        for sentence in sentences:
            if not self.verify_sentence_grounding(sentence, context):
                external_sentences.append(sentence)
        
        return external_sentences
    
    def generate_grounding_report(self, answer: str, context: str) -> Dict[str, Any]:
        """Generate comprehensive grounding report"""
        is_grounded, analysis = self.verify_answer_grounding(answer, context)
        external_knowledge = self.detect_external_knowledge(answer, context)
        
        return {
            'answer': answer,
            'context_length': len(context),
            'answer_length': len(answer),
            'is_grounded': is_grounded,
            'grounding_analysis': analysis,
            'external_knowledge_detected': len(external_knowledge) > 0,
            'external_sentences': external_knowledge,
            'recommendation': self.get_recommendation(is_grounded, analysis)
        }
    
    def get_recommendation(self, is_grounded: bool, analysis: Dict[str, Any]) -> str:
        """Get recommendation based on grounding analysis"""
        if is_grounded:
            return "Answer is properly grounded in context"
        elif analysis['grounded_ratio'] >= 0.5:
            return "Answer partially grounded - consider revision"
        else:
            return "Answer not grounded - regenerate with stricter context enforcement"
