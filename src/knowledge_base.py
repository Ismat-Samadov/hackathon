"""
Knowledge Base Module - Store and retrieve processed documents.

This module provides an in-memory knowledge base for storing and searching
extracted document content. It can be extended to use vector databases
like ChromaDB, FAISS, Pinecone, or PostgreSQL with pgvector.

Current implementation uses simple keyword matching for search.
Future versions will implement vector similarity search using embeddings.
"""

from typing import Dict, List, Optional
import logging

from src.config import settings
from src.models import Source, PageOCR
from src.llm_client import get_client

# Setup logging
logger = logging.getLogger(__name__)


# ============================================================================
# In-Memory Knowledge Base
# ============================================================================

class KnowledgeBase:
    """
    In-memory knowledge base for storing and retrieving documents.

    Stores extracted PDF pages indexed by document name. Provides search
    functionality using keyword matching. Can be extended to support
    vector similarity search with embeddings.
    """

    def __init__(self) -> None:
        """Initialize an empty knowledge base."""
        # Maps PDF filename to list of pages with content
        self.documents: Dict[str, List[Dict]] = {}

    def add_document(self, pdf_name: str, pages: List[PageOCR]) -> None:
        """
        Add a processed document to the knowledge base.

        Args:
            pdf_name: Name of the PDF document
            pages: List of PageOCR objects with extracted content
        """
        self.documents[pdf_name] = [
            {"page_number": p.page_number, "content": p.MD_text}
            for p in pages
        ]
        logger.info(
            f"Added document '{pdf_name}' with {len(pages)} pages "
            f"to knowledge base"
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_content_length: int = 1500
    ) -> List[Source]:
        """
        Search for relevant documents using keyword matching.

        Performs a simple word-based search across all stored documents.
        Results are ranked by the number of matching keywords found.

        Note: TODO - Implement vector similarity search using embeddings
        for better semantic matching.

        Args:
            query: Search query string
            top_k: Maximum number of results to return
            max_content_length: Maximum characters to include in each result

        Returns:
            List of Source objects ranked by relevance
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Search across all documents
        for pdf_name, pages in self.documents.items():
            for page in pages:
                content = page["content"]
                content_lower = content.lower()

                # Score based on keyword matches
                matches = sum(
                    1 for word in query_words
                    if word in content_lower
                )

                if matches > 0:
                    # Truncate content if necessary
                    truncated_content = content[:max_content_length]
                    if len(content) > max_content_length:
                        truncated_content += "..."

                    results.append({
                        "score": matches,
                        "source": Source(
                            pdf_name=pdf_name,
                            page_number=page["page_number"],
                            content=truncated_content
                        )
                    })

        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        logger.debug(
            f"Search for '{query}' found {len(results)} results, "
            f"returning top {top_k}"
        )
        return [r["source"] for r in results[:top_k]]

    def get_status(self) -> Dict:
        """
        Get knowledge base status summary.

        Returns:
            Dictionary with statistics about stored documents
        """
        total_pages = sum(len(pages) for pages in self.documents.values())
        return {
            "documents_count": len(self.documents),
            "total_pages": total_pages,
            "documents": [
                {"name": name, "pages": len(pages)}
                for name, pages in self.documents.items()
            ]
        }

    def clear(self) -> None:
        """Clear all documents from the knowledge base."""
        self.documents.clear()
        logger.info("Cleared all documents from knowledge base")


# ============================================================================
# Global Knowledge Base Instance
# ============================================================================

knowledge_base = KnowledgeBase()


# ============================================================================
# Embedding Functions (for future vector search)
# ============================================================================

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for a list of texts.

    Uses Cohere-embed-v3-multilingual model for multilingual support
    including Azerbaijani and Russian.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors

    Note:
        This function requires the embedding endpoint to be available
        in the Azure AI Foundry configuration.
    """
    client = get_client()

    try:
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]
        logger.debug(f"Generated embeddings for {len(texts)} texts")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        return []


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    Split text into overlapping chunks.

    Useful for breaking large documents into smaller segments for
    embedding or processing.

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks

    Example:
        >>> text = "Long text..."
        >>> chunks = chunk_text(text, chunk_size=500, overlap=50)
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks
