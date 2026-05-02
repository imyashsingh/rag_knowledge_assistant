from typing import Optional, Dict, Any
from openai import OpenAI
from app.config import settings
import json

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generate_response(
    prompt: str,
    model: str = "llama3-8b-8192",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Optional[str]:
    """
    Generate response from Groq LLM

    Args:
        prompt: The prompt to send to the LLM
        model: Model to use (default: llama3-8b-8192)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response

    Returns:
        Generated text or None if error
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating LLM response: {str(e)}")
        return None


def build_rag_prompt(query: str, context_chunks: list[str]) -> str:
    """
    Build RAG prompt with context and query

    Args:
        query: User's question
        context_chunks: List of relevant text chunks

    Returns:
        Formatted prompt for LLM
    """
    context = "\n\n".join(
        [f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])

    prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context. If the context doesn't contain enough information to answer the question, say so politely.

{context}

Question: {query}

Instructions:
1. Use only the provided context to answer the question
2. If the context doesn't contain the answer, say "I don't have enough information to answer this question based on the provided context."
3. Be concise and accurate
4. If you use information from the context, cite the source by mentioning "according to the provided context"

Answer:"""

    return prompt


def generate_chat_response(
    query: str,
    context_chunks: list[str],
    model: str = "llama3-8b-8192"
) -> Optional[str]:
    """
    Generate response for RAG chat

    Args:
        query: User's question
        context_chunks: List of relevant text chunks
        model: LLM model to use

    Returns:
        Generated response or None if error
    """
    prompt = build_rag_prompt(query, context_chunks)
    return generate_response(prompt, model=model)


def get_available_models() -> list[str]:
    """Get list of available Groq models"""
    return [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]


def validate_api_key() -> bool:
    """Check if Groq API key is valid"""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return True
    except Exception:
        return False
