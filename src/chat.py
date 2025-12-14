"""
Chat Module - Generate intelligent responses using LLM with retrieved context.

This module handles chat request processing by:
1. Extracting the user's latest query from chat history
2. Searching the knowledge base for relevant context
3. Generating a response using the LLM with the retrieved context
4. Returning both the answer and source documents
"""

import logging
from typing import List

from src.config import settings
from src.llm_client import get_client
from src.models import ChatMessage, Source, ChatResponse
from src.knowledge_base import knowledge_base

# Setup logging
logger = logging.getLogger(__name__)


# ============================================================================
# System Prompt
# ============================================================================

SYSTEM_PROMPT = """You are an expert assistant for SOCAR's historical document archive and knowledge base.
Your mission is to make decades of valuable oil and gas research data accessible and searchable.

You help users discover and understand information from historical research documents spanning multiple languages and scripts:
- Azerbaijani (Latin and Cyrillic scripts)
- Russian
- Handwritten and printed documents

## Core Instructions:

1. **Answer Accuracy**: Provide precise, technically accurate answers based ONLY on the provided source documents
2. **Citation Management**:
   - Always reference the specific PDF name and page number
   - Provide relevant extracted text snippets to support your answer
   - Ensure citations are complete and verifiable
3. **Answer Quality**: Construct answers that are coherent, contextually relevant, and directly address the user's question
4. **Language Support**: Respond in the language of the question (Azerbaijani, Russian, or English)
5. **Source Handling**:
   - If information is not found in sources, explicitly state: "This information is not available in the provided documents"
   - When multiple sources are relevant, prioritize by relevance and coherence
   - Preserve technical terminology from oil and gas domain

## Evaluation Criteria (Your answers will be judged on):
- **Answer**: How accurately your response matches the correct information
- **Citation Relevance**: How relevant the retrieved chunks are to answering the question
- **Citation Order**: How logically the sources are arranged to support your answer

## Source Documents:
The following extracted documents and pages will be provided in the context. Use them to construct comprehensive, well-cited answers."""


# ============================================================================
# Helper Functions
# ============================================================================

def _build_context(sources: List[Source]) -> str:
    """
    Build context string from retrieved sources.

    Args:
        sources: List of Source objects to include in context

    Returns:
        Formatted context string with source documents
    """
    if not sources:
        return "No relevant documents found in the knowledge base."

    context = "## Retrieved Source Documents:\n\n"
    for i, src in enumerate(sources, 1):
        context += f"### Source {i}: {src.pdf_name} (Page {src.page_number})\n"
        context += f"{src.content}\n\n"

    return context


def _generate_response(
    messages: List[ChatMessage],
    sources: List[Source],
    model: str | None = None
) -> str:
    """
    Generate a response using the LLM with retrieved context.

    Args:
        messages: Chat history (list of ChatMessage objects)
        sources: Retrieved source documents from knowledge base
        model: Model to use (defaults to settings.CHAT_MODEL)

    Returns:
        Generated response text from the LLM
    """
    if model is None:
        model = settings.CHAT_MODEL

    client = get_client()
    context = _build_context(sources)

    # Build messages for the API
    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}
    ]

    # Add chat history
    for msg in messages:
        api_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            max_completion_tokens=2000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Error generating response: {str(e)}"


# ============================================================================
# Chat Function
# ============================================================================

def chat(messages: List[ChatMessage]) -> ChatResponse:
    """
    Process a chat request and generate a response.

    Workflow:
    1. Extract the latest user message from chat history
    2. Search the knowledge base for relevant context
    3. Generate a response using the LLM
    4. Return both answer and source documents

    Args:
        messages: List of chat messages (conversation history + current message)

    Returns:
        ChatResponse with generated answer and source documents
    """
    # Extract user messages from history
    user_messages = [m for m in messages if m.role == "user"]

    if not user_messages:
        logger.warning("No user message found in chat history")
        return ChatResponse(
            sources=[],
            answer="No user message found in chat history."
        )

    # Get the latest user query
    latest_query = user_messages[-1].content
    logger.info(f"Processing chat query: {latest_query[:100]}...")

    # Search knowledge base for relevant documents
    sources = knowledge_base.search(latest_query, top_k=settings.TOP_K_RESULTS)
    logger.info(f"Retrieved {len(sources)} sources from knowledge base")

    # Generate response with context
    answer = _generate_response(messages, sources)

    return ChatResponse(sources=sources, answer=answer)
