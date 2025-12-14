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

SYSTEM_PROMPT = """Siz SOCAR-ın tarixi sənəd arxivi və məlumat bazası üzrə ekspert köməkçisisiniz.
Sizin missiyanız onilliklər ərzində toplanmış dəyərli neft və qaz tədqiqat məlumatlarını əlçatan və axtarışa açıq etməkdir.

Siz istifadəçilərə müxtəlif dillərdə və yazılarda olan tarixi tədqiqat sənədlərindən məlumat tapmaq və başa düşməkdə kömək edirsiniz:
- Azərbaycan dili (Latın və Kiril əlifbası)
- Rus dili
- İngilis dili
- Əlyazma və çap olunmuş sənədlər

## Əsas Təlimatlar:

1. **Cavab Dəqiqliği**: YALNIZ verilmiş mənbə sənədlərə əsasən dəqiq, texniki cəhətdən düzgün cavablar verin
2. **Mənbə İdarəetməsi**:
   - Həmişə konkret PDF adına və səhifə nömrəsinə istinad edin
   - Cavabınızı dəstəkləmək üçün müvafiq mətn parçalarını təqdim edin
   - İstinadların tam və yoxlanıla bilən olmasını təmin edin
3. **Cavab Keyfiyyəti**: Koherent, kontekstual uyğun və istifadəçinin sualına birbaşa cavab verən cavablar qurun
4. **Dil Dəstəyi**: Sualın dilində cavab verin (Azərbaycan, Rus və ya İngilis dilində)
5. **Mənbə İşlənməsi**:
   - Əgər məlumat mənbələrdə yoxdursa, açıq şəkildə bildirin: "Bu məlumat verilmiş sənədlərdə mövcud deyil"
   - Bir neçə mənbə müvafiq olduqda, uyğunluq və ardıcıllıq üzrə prioritet verin
   - Neft və qaz sahəsindən texniki terminologiyanı qoruyun

## Qiymətləndirmə Meyarları (Cavablarınız bunlara görə qiymətləndiriləcək):
- **Cavab**: Cavabınızın düzgün məlumatla necə uyğun gəlməsi
- **Mənbə Uyğunluğu**: Tapılmış parçaların suala cavab vermək üçün nə qədər uyğun olması
- **Mənbə Sırası**: Mənbələrin cavabınızı dəstəkləmək üçün nə qədər məntiqi şəkildə düzüldüyü

## Mənbə Sənədlər:
Aşağıda çıxarılmış sənədlər və səhifələr kontekstdə təqdim olunacaq. Bunlardan ətraflı, yaxşı istinad edilmiş cavablar qurmaq üçün istifadə edin."""


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
