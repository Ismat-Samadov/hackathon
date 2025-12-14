"""
Knowledge Base Module - Store and retrieve processed documents using Pinecone.

This module provides a vector-based knowledge base for storing and searching
extracted document content using Pinecone vector database and embeddings.
Supports efficient semantic search using BAAI/bge-large-en-v1.5 embeddings.
"""

from typing import Dict, List
import logging
import hashlib
import time

from src.config import settings
from src.models import Source, PageOCR

# Setup logging
logger = logging.getLogger(__name__)

# Global embedding model (lazy loaded)
embedding_model = None


# ============================================================================
# Embedding Model (Local)
# ============================================================================

def get_embedding_model():
    """
    Lazy load embedding model.
    
    Uses BAAI/bge-large-en-v1.5 locally for best performance.
    This is open-source and deployable (higher hackathon scores).
    
    Returns:
        SentenceTransformer model instance
    """
    global embedding_model
    if embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"Embedding model loaded (dimension: {embedding_model.get_sentence_embedding_dimension()})")
    return embedding_model


# ============================================================================
# Pinecone Vector Database Integration
# ============================================================================

class KnowledgeBase:
    """
    Pinecone-based knowledge base for storing and retrieving documents.

    Uses vector embeddings for semantic search across document chunks.
    Provides superior search quality compared to keyword matching.
    """

    def __init__(self) -> None:
        """Initialize Pinecone knowledge base."""
        from pinecone import Pinecone, ServerlessSpec
        
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        
        # Get or create index
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            # Get embedding dimension from a test embedding
            test_embedding = self._get_embeddings(["test"])[0]
            dimension = len(test_embedding)
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION
                )
            )
            # Wait for index to be ready
            time.sleep(1)
        
        self.index = self.pc.Index(self.index_name)
        logger.info(f"Connected to Pinecone index: {self.index_name}")

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using local BAAI/bge-large-en-v1.5 model.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (1024 dimensions)
        """
        try:
            model = get_embedding_model()
            embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            # Convert numpy arrays to lists for JSON serialization
            embeddings = [emb.tolist() for emb in embeddings]
            logger.debug(f"Generated embeddings for {len(texts)} texts using local model")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters (defaults to settings)
            overlap: Number of overlapping characters (defaults to settings)

        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if overlap is None:
            overlap = settings.CHUNK_OVERLAP

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

    def _generate_id(self, pdf_name: str, page_number: int, chunk_index: int) -> str:
        """
        Generate a unique ID for a document chunk.

        Args:
            pdf_name: Name of the PDF
            page_number: Page number
            chunk_index: Index of the chunk within the page

        Returns:
            Unique identifier string
        """
        content = f"{pdf_name}::{page_number}::{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()

    def add_document(self, pdf_name: str, pages: List[PageOCR]) -> None:
        """
        Add a processed document to the knowledge base.

        Chunks the document, generates embeddings, and stores in Pinecone.

        Args:
            pdf_name: Name of the PDF document
            pages: List of PageOCR objects with extracted content
        """
        vectors_to_upsert = []
        
        for page in pages:
            # Chunk the page content
            chunks = self._chunk_text(page.MD_text)
            
            if not chunks:
                continue
            
            # Get embeddings for all chunks
            embeddings = self._get_embeddings(chunks)
            
            # Prepare vectors for upsert
            for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = self._generate_id(pdf_name, page.page_number, chunk_idx)
                
                metadata = {
                    "pdf_name": pdf_name,
                    "page_number": page.page_number,
                    "content": chunk,
                    "chunk_index": chunk_idx
                }
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
        
        # Batch upsert to Pinecone
        if vectors_to_upsert:
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(
                f"Added document '{pdf_name}' with {len(pages)} pages "
                f"and {len(vectors_to_upsert)} chunks to Pinecone"
            )

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_content_length: int = 1500
    ) -> List[Source]:
        """
        Search for relevant documents using vector similarity.

        Args:
            query: Search query string
            top_k: Maximum number of results to return
            max_content_length: Maximum characters to include in each result

        Returns:
            List of Source objects ranked by relevance
        """
        # Get query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Convert to Source objects
        sources = []
        for match in results.matches:
            metadata = match.metadata
            content = metadata.get("content", "")
            
            # Truncate content if necessary
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            sources.append(Source(
                pdf_name=metadata.get("pdf_name", ""),
                page_number=metadata.get("page_number", 0),
                content=content
            ))
        
        logger.debug(f"Search for '{query}' found {len(sources)} results")
        return sources

    def get_unique_pdfs(self) -> Dict[str, Dict]:
        """
        Get list of unique PDFs indexed in Pinecone with their page counts.

        Returns:
            Dictionary mapping pdf_name to {"pages": set_of_page_numbers}
        """
        pdf_info = {}
        pagination_token = None
        
        try:
            while True:
                results = self.index.list_paginated(limit=100, pagination_token=pagination_token)
                vector_ids = [v.id for v in results.vectors]
                
                if not vector_ids:
                    break
                
                # Fetch metadata
                fetch_response = self.index.fetch(ids=vector_ids)
                
                for vec_id, vector_data in fetch_response.vectors.items():
                    if hasattr(vector_data, 'metadata') and vector_data.metadata:
                        if 'pdf_name' in vector_data.metadata:
                            pdf_name = vector_data.metadata['pdf_name']
                            
                            if pdf_name not in pdf_info:
                                pdf_info[pdf_name] = {"pages": set()}
                            
                            if 'page_number' in vector_data.metadata:
                                pdf_info[pdf_name]["pages"].add(vector_data.metadata['page_number'])
                
                # Check for next page
                if hasattr(results, 'pagination') and hasattr(results.pagination, 'next') and results.pagination.next:
                    pagination_token = results.pagination.next
                else:
                    break
            
            # Convert sets to counts for JSON serialization
            for pdf_name in pdf_info:
                pdf_info[pdf_name] = {"page_count": len(pdf_info[pdf_name]["pages"])}
            
            return pdf_info
            
        except Exception as e:
            logger.error(f"Error getting unique PDFs: {e}")
            return {}

    def get_status(self) -> Dict:
        """
        Get knowledge base status summary including list of indexed PDFs.

        Returns:
            Dictionary with statistics about stored vectors and list of PDFs
        """
        try:
            stats = self.index.describe_index_stats()
            
            # Handle both dict and object responses
            if isinstance(stats, dict):
                total_vectors = stats.get('total_vector_count', 0)
                dimension = stats.get('dimension', 'unknown')
            else:
                total_vectors = getattr(stats, 'total_vector_count', 0)
                dimension = getattr(stats, 'dimension', 'unknown')
            
            # Get unique PDFs
            pdfs = self.get_unique_pdfs()
            
            return {
                "total_vectors": total_vectors,
                "index_name": self.index_name,
                "dimension": dimension,
                "pdf_count": len(pdfs),
                "pdfs": pdfs
            }
        except Exception as e:
            logger.error(f"Error getting index status: {e}")
            return {
                "total_vectors": 0,
                "index_name": self.index_name,
                "dimension": "unknown",
                "pdf_count": 0,
                "pdfs": {},
                "error": str(e)
            }

    def ingest_pdf(self, pdf_name: str, pages: List[PageOCR]) -> Dict:
        """
        Ingest a single PDF document into Pinecone.

        Args:
            pdf_name: Name of the PDF document
            pages: List of PageOCR objects with extracted content

        Returns:
            Dictionary with ingestion statistics
        """
        chunks_added = 0
        pages_processed = 0
        
        try:
            for page in pages:
                # Chunk the page content
                chunks = self._chunk_text(page.MD_text)
                
                if not chunks:
                    continue
                
                # Get embeddings for all chunks
                embeddings = self._get_embeddings(chunks)
                
                vectors_to_upsert = []
                for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    vector_id = self._generate_id(pdf_name, page.page_number, chunk_idx)
                    
                    metadata = {
                        "pdf_name": pdf_name,
                        "page_number": page.page_number,
                        "content": chunk,
                        "chunk_index": chunk_idx
                    }
                    
                    vectors_to_upsert.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    })
                
                # Upsert to Pinecone
                if vectors_to_upsert:
                    self.index.upsert(vectors=vectors_to_upsert)
                    chunks_added += len(vectors_to_upsert)
                    pages_processed += 1
            
            logger.info(f"Ingested {pdf_name}: {pages_processed} pages, {chunks_added} chunks")
            
            return {
                "status": "success",
                "pdf_name": pdf_name,
                "pages_processed": pages_processed,
                "chunks_added": chunks_added
            }
            
        except Exception as e:
            logger.error(f"Error ingesting {pdf_name}: {e}")
            return {
                "status": "error",
                "pdf_name": pdf_name,
                "error": str(e)
            }

    def clear(self) -> None:
        """Clear all vectors from the knowledge base."""
        # Delete all vectors by namespace (default namespace is '')
        self.index.delete(delete_all=True)
        logger.info("Cleared all vectors from Pinecone index")


# ============================================================================
# Global Knowledge Base Instance
# ============================================================================

logger.info("Initializing Pinecone knowledge base")
knowledge_base = KnowledgeBase()


# ============================================================================
# Helper Functions
# ============================================================================

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for a list of texts using local BAAI/bge-large-en-v1.5 model.

    Uses sentence-transformers for local embedding generation.
    This is open-source and deployable (preferred for hackathon scoring).

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (1024 dimensions)

    Note:
        Model is loaded locally using sentence-transformers library.
    """
    try:
        model = get_embedding_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Convert numpy arrays to lists for JSON serialization
        embeddings = [emb.tolist() for emb in embeddings]
        logger.debug(f"Generated embeddings for {len(texts)} texts using local model")
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
