"""
SOCAR Historical Document Processing API.

REST API endpoints for historical document processing:
- POST /ocr: Extract text from PDF documents with parallel processing
- POST /chat: Query the knowledge base with conversation history
- GET /: Health check and API information
- GET /models: List configured models
- GET /knowledge-base/status: Knowledge base statistics
- DELETE /knowledge-base/clear: Clear all documents

Features:
- OCR: Llama-4-Maverick-17B-128E-Instruct-FP8 (multimodal)
- Chat: Llama-4-Maverick-17B-128E-Instruct-FP8
- Embeddings: Cohere-embed-v3-multilingual
- Multilingual support: Azerbaijani (Latin/Cyrillic), Russian, English
"""

import logging
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.config import settings
from src.models import PageOCR, ChatMessage, ChatResponse
from src.ocr import process_pdf_async
from src.chat import chat
from src.knowledge_base import knowledge_base
from src.response_logger import get_logger

# Setup logging
logger = logging.getLogger(__name__)


# ============================================================================
# FastAPI Application Configuration
# ============================================================================

app = FastAPI(
    title="SOCAR Document Processing API",
    description="""
    RESTful API for historical document processing with OCR and RAG-powered chat.

    ## Key Features

    - **Document OCR**: Extract text from PDF documents
      - Supports Azerbaijani (Latin & Cyrillic), Russian, English
      - Handles handwritten and printed documents
      - Parallel processing for fast multi-page extraction

    - **Knowledge Base Search**: Query extracted documents
      - Intelligent context retrieval
      - LLM-powered response generation
      - Citation tracking with page references

    - **Multilingual Support**: Process documents in multiple languages
      - Azerbaijani (Latin script): ə, ç, ğ, ı, ö, ş, ü
      - Azerbaijani (Cyrillic script): Inherited from Russian
      - Russian: Full Cyrillic alphabet support
      - English: Standard Latin alphabet

    ## API Endpoints

    - `POST /ocr`: Extract text from PDF files
    - `POST /chat`: Query knowledge base with chat history
    - `GET /`: API health check and information
    - `GET /models`: List configured AI models
    - `GET /knowledge-base/status`: Knowledge base statistics
    - `DELETE /knowledge-base/clear`: Clear all documents
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors gracefully.

    Provides user-friendly error messages instead of exposing validation details.

    Args:
        request: The HTTP request that failed validation
        exc: The validation error

    Returns:
        JSON response with error message
    """
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": ["body"],
                    "msg": "Invalid request format. Please check your input.",
                    "type": "value_error"
                }
            ]
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    Handle HTTP exceptions with consistent formatting.

    Args:
        request: The HTTP request
        exc: The HTTP exception

    Returns:
        JSON response with error details
    """
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# ============================================================================
# Health Check & Information Endpoints
# ============================================================================

@app.get("/")
async def root() -> dict:
    """
    Health check and API information endpoint.

    Returns:
        Dictionary with API status and available endpoints
    """
    return {
        "status": "running",
        "api": "SOCAR Document Processing",
        "version": "1.0.0",
        "endpoints": {
            "ocr": "POST /ocr - Upload PDF for text extraction",
            "chat": "POST /chat - Query the knowledge base",
            "models": "GET /models - List configured models",
            "kb_status": "GET /knowledge-base/status - Knowledge base statistics",
            "docs": "GET /docs - Swagger UI documentation",
        },
        "models": {
            "ocr": settings.OCR_MODEL,
            "chat": settings.CHAT_MODEL,
            "embedding": settings.EMBEDDING_MODEL,
        }
    }


@app.get("/models")
async def list_models() -> dict:
    """
    List all configured AI models.

    Returns:
        Dictionary with model names and configuration notes
    """
    return {
        "ocr_model": settings.OCR_MODEL,
        "chat_model": settings.CHAT_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "note": (
            "Set environment variables to change models: "
            "OCR_MODEL, CHAT_MODEL, EMBEDDING_MODEL"
        )
    }


# ============================================================================
# OCR Endpoint
# ============================================================================

@app.post("/ocr", response_model=List[PageOCR])
async def ocr_endpoint(file: UploadFile = File(...)) -> List[PageOCR]:
    """
    Extract text from PDF documents using vision models.

    Processes PDF files page-by-page using parallel async processing
    for optimal performance on multi-page documents.

    **Request**: Multipart form data with PDF file
    **Response**: Array of PageOCR objects with extracted text

    Args:
        file: PDF file to process

    Returns:
        List of PageOCR objects with extracted text for each page

    Raises:
        HTTPException: 400 if file is not a PDF, 500 if processing fails

    Example:
        ```bash
        curl -X POST \\
          -F "file=@document.pdf" \\
          http://localhost:8000/ocr
        ```

        Response:
        ```json
        [
            {
                "page_number": 1,
                "MD_text": "# Document Title\\n\\nExtracted content..."
            },
            {
                "page_number": 2,
                "MD_text": "More content..."
            }
        ]
        ```
    """
    response_logger = get_logger()

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    try:
        logger.info(f"Starting OCR processing for: {file.filename}")

        # Read PDF file
        pdf_bytes = await file.read()

        # Process with parallel async extraction
        results = await process_pdf_async(pdf_bytes, file.filename)

        logger.info(
            f"OCR completed for {file.filename}: "
            f"{len(results)} pages extracted"
        )

        # Log results
        for result in results:
            response_logger.log_ocr_request(
                filename=file.filename,
                page_number=result.page_number,
                extracted_text=result.MD_text,
                metadata={"text_length": len(result.MD_text)}
            )

        # Add to knowledge base for later querying
        ingest_result = knowledge_base.ingest_pdf(file.filename, results)
        logger.info(f"Indexed to Pinecone: {ingest_result}")

        return results

    except Exception as e:
        logger.error(f"OCR processing failed for {file.filename}: {str(e)}")
        response_logger.log_error(
            "ocr",
            str(e),
            {"filename": file.filename}
        )
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )


# ============================================================================
# Chat Endpoint
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(messages: List[ChatMessage]) -> ChatResponse:
    """
    Query the knowledge base with conversation history.

    Processes user queries against stored documents and generates
    context-aware responses using the configured LLM.

    **Request**: JSON array of chat messages
    **Response**: ChatResponse with sources and generated answer

    Args:
        messages: List of ChatMessage objects (conversation history)

    Returns:
        ChatResponse with retrieved sources and generated answer

    Raises:
        HTTPException: 400 if input invalid, 500 if processing fails

    Example:
        ```bash
        curl -X POST http://localhost:8000/chat \\
          -H "Content-Type: application/json" \\
          -d '[{"role": "user", "content": "What is the document about?"}]'
        ```

        Response:
        ```json
        {
            "sources": [
                {
                    "pdf_name": "report.pdf",
                    "page_number": 1,
                    "content": "..."
                }
            ],
            "answer": "Based on the provided sources, the document..."
        }
        ```
    """
    response_logger = get_logger()

    # Validate input
    if not messages:
        logger.warning("Empty chat history received")
        raise HTTPException(
            status_code=400,
            detail="Chat history cannot be empty"
        )

    # Extract user messages
    user_messages = [m for m in messages if m.role == "user"]
    if not user_messages:
        logger.warning("No user messages in chat history")
        raise HTTPException(
            status_code=400,
            detail="At least one user message is required"
        )

    try:
        logger.info(f"Processing chat with {len(messages)} messages")

        # Generate response
        response = chat(messages)

        logger.info(
            f"Chat response generated with {len(response.sources)} sources"
        )

        # Log interaction
        response_logger.log_chat_request(
            messages=[
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            answer=response.answer,
            sources=response.sources,
            metadata={"sources_count": len(response.sources)}
        )

        return response

    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        response_logger.log_error(
            "chat",
            str(e),
            {"message_count": len(messages)}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


# ============================================================================
# Knowledge Base Management Endpoints
# ============================================================================

@app.get("/knowledge-base/status")
async def knowledge_base_status() -> dict:
    """
    Get knowledge base status and statistics including list of indexed PDFs.

    Returns:
        Dictionary with vector count, PDF list, and dimension info
        
    Example Response:
        {
            "total_vectors": 1245,
            "index_name": "hackathon",
            "dimension": 1024,
            "pdf_count": 28,
            "pdfs": {
                "document1.pdf": {"page_count": 15},
                "document2.pdf": {"page_count": 12}
            }
        }
    """
    status = knowledge_base.get_status()
    logger.debug(
        f"Knowledge base status: {status.get('total_vectors', 0)} vectors, "
        f"{status.get('pdf_count', 0)} PDFs in index '{status.get('index_name', 'unknown')}'"
    )
    return status


@app.post("/knowledge-base/ingest")
async def ingest_pdf_endpoint(file: UploadFile = File(...)) -> dict:
    """
    Ingest a PDF directly into the knowledge base.
    
    This endpoint:
    1. Performs OCR on the PDF
    2. Chunks the text
    3. Generates embeddings
    4. Stores in Pinecone with metadata
    
    Args:
        file: PDF file to ingest
        
    Returns:
        Dictionary with ingestion statistics
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    try:
        logger.info(f"Ingesting PDF: {file.filename}")
        
        # Read and process PDF
        pdf_bytes = await file.read()
        pages = await process_pdf_async(pdf_bytes, file.filename)
        
        # Ingest into Pinecone
        result = knowledge_base.ingest_pdf(file.filename, pages)
        
        logger.info(f"Ingestion complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.delete("/knowledge-base/clear")
async def clear_knowledge_base() -> dict:
    """
    Clear all documents from the knowledge base.

    Warning: This action cannot be undone!

    Returns:
        Dictionary with confirmation message
    """
    logger.warning("Knowledge base clear requested")
    knowledge_base.clear()
    return {"status": "cleared", "message": "All documents removed"}


# ============================================================================
# Server Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    logger.info("SOCAR API starting up")
    logger.info(f"OCR Model: {settings.OCR_MODEL}")
    logger.info(f"Chat Model: {settings.CHAT_MODEL}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on application shutdown."""
    logger.info("SOCAR API shutting down")
