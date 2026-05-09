from typing import Optional, Dict, Any
from openai import OpenAI
from app.config import settings

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generate_response(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
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


def build_rag_prompt(query: str, context_chunks: list[str], conversation_history: list[dict] = None) -> str:
    """
    Build RAG prompt with context and query

    Args:
        query: User's question
        context_chunks: List of relevant text chunks
        conversation_history: Optional list of previous messages in the conversation

    Returns:
        Formatted prompt for LLM
    """
    context = "\n\n".join(
        [f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])

    # Build conversation history section if provided
    conversation_section = ""
    if conversation_history and len(conversation_history) > 0:
        conversation_lines = []
        for msg in conversation_history:
            # Handle both Pydantic objects and dictionaries
            if hasattr(msg, 'role'):
                # It's a Pydantic object
                role = "User" if msg.role == "user" else "Assistant"
                content = msg.content if hasattr(msg, 'content') else ""
            else:
                # It's a dictionary
                role = "User" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")
            conversation_lines.append(f"{role}: {content}")
        conversation_text = "\n".join(conversation_lines)
        conversation_section = f"CONVERSATION HISTORY:\n{conversation_text}\n"

    prompt = f"""You are a helpful AI assistant that answers questions based primarily on document context, with awareness of conversation history.

CONTEXT:
{context}

{conversation_section}
USER QUESTION: {query}

INSTRUCTIONS:
1. First and foremost, answer based on the CONTEXT above. The document context is your primary source of information.
2. Use the conversation history only to understand if this is a follow-up question or to maintain conversational flow.
3. If the user asks for clarification or examples about something you already explained, provide additional examples from the context or explain differently.
4. Provide a direct, accurate answer based primarily on the document context.
5. Write in a natural, conversational style - avoid technical references like "Context 1", "Context 2", etc.
6. If the context doesn't contain the answer, clearly state: "I don't have enough information to answer this question based on the available documents."
7. Be concise but thorough - provide a complete answer in 2-4 sentences when possible.
8. Do not make up information or use external knowledge.
9. Focus on providing a helpful, easy-to-understand answer.
10. Use simple, clear language that anyone can understand.

ANSWER:"""
    return prompt


def generate_chat_response(
    query: str,
    context_chunks: list[str],
    conversation_history: list[dict] = None,
    model: str = "llama-3.1-8b-instant"
) -> Optional[str]:
    """
    Generate response for RAG chat

    Args:
        query: User's question
        context_chunks: List of relevant text chunks
        conversation_history: Optional list of previous messages in the conversation
        model: LLM model to use

    Returns:
        Generated response or None if error
    """
    prompt = build_rag_prompt(query, context_chunks, conversation_history)
    return generate_response(prompt, model=model, max_tokens=1500)


def get_available_models() -> list[str]:
    """Get list of available Groq models"""
    return [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "llama-3.1-405b-reasoning",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]


def validate_api_key() -> bool:
    """Check if Groq API key is valid"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return True
    except Exception:
        return False
