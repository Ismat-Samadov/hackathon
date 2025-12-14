"""
SOCAR Historical Document Processing API

Two REST API endpoints:
1. OCR Endpoint - POST /ocr - Extract text from PDF documents
2. LLM Endpoint - POST /chat - Query the knowledge base with chat history

Uses open-source models (preferred for higher scores):
- OCR: Llama-4-Maverick-17B-128E-Instruct-FP8 (multimodal, best quality)
- Chat: Llama-4-Maverick-17B-128E-Instruct-FP8
- Embeddings: Cohere-embed-v3-multilingual
"""

import os
import base64
import json
import io
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import fitz  # PyMuPDF
from dotenv import load_dotenv
from openai import AzureOpenAI
from PIL import Image

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

BASE_URL = os.getenv("BASE_URL", "https://llmapihackathon.services.ai.azure.com/")
API_KEY = os.getenv("API_KEY")

# Model configuration (Open Source preferred)
# Llama-4-Maverick supports both text AND vision - best for OCR!
OCR_MODEL = os.getenv("OCR_MODEL", "Llama-4-Maverick-17B-128E-Instruct-FP8")
CHAT_MODEL = os.getenv("CHAT_MODEL", "Llama-4-Maverick-17B-128E-Instruct-FP8")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Cohere-embed-v3-multilingual")

# OCR settings
OCR_DPI_SCALE = float(os.getenv("OCR_DPI_SCALE", "1.5"))  # 1.5x balance quality/size
OCR_MAX_TOKENS = int(os.getenv("OCR_MAX_TOKENS", "4000"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "90"))  # JPEG compression quality

# ============================================================================
# Pydantic Models
# ============================================================================


class PageOCR(BaseModel):
    """OCR result for a single page."""

    page_number: int
    MD_text: str


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str  # "user" or "assistant"
    content: str


class Source(BaseModel):
    """A source reference."""

    pdf_name: str
    page_number: int
    content: str


class ChatResponse(BaseModel):
    """Response from the LLM endpoint."""

    sources: List[Source]
    answer: str


# ============================================================================
# Initialize FastAPI
# ============================================================================

app = FastAPI(
    title="SOCAR Document Processing API",
    description="OCR and Chat endpoints for historical document processing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Azure OpenAI Client
# ============================================================================


def get_client() -> AzureOpenAI:
    """Create Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=BASE_URL,
        api_key=API_KEY,
        api_version="2024-12-01-preview",
    )


# ============================================================================
# OCR Functions
# ============================================================================

OCR_PROMPT = """You are an expert OCR system specialized in extracting text from documents.

Extract ALL text from this document image accurately. The document may contain:
- Azerbaijani text (Latin script)
- Azerbaijani text (Cyrillic script)  
- Russian text
- Technical/scientific terminology (oil and gas engineering)
- Handwritten notes
- Tables, figures, and diagrams

Instructions:
1. Preserve the original document structure (headings, paragraphs, lists, tables)
2. Output in clean Markdown format
3. For tables, use Markdown table syntax
4. For unclear or illegible text, use [unclear] marker
5. Preserve any numbers, dates, and technical terms exactly
6. Do NOT add any commentary - only output the extracted text

Output the extracted Markdown text:"""


def pdf_page_to_base64(
    page: fitz.Page, scale: float = 1.5, jpeg_quality: int = 90
) -> tuple[str, str]:
    """Convert a PDF page to base64-encoded JPEG image for smaller size.

    Returns: (base64_data, mime_type)
    """
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat)

    # Convert to JPEG for smaller size (better for API calls)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=jpeg_quality)
    image_bytes = buffer.getvalue()

    return base64.b64encode(image_bytes).decode("utf-8"), "image/jpeg"


def extract_text_with_vision(
    client: AzureOpenAI,
    image_base64: str,
    mime_type: str = "image/jpeg",
    model: str = None,
) -> str:
    """Use vision model to extract text from an image."""
    if model is None:
        model = OCR_MODEL

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": OCR_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=OCR_MAX_TOKENS,
            # temperature=0.1,  # Low temperature for accuracy
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OCR Error: {str(e)}]"


def process_pdf_ocr(pdf_bytes: bytes, filename: str) -> List[PageOCR]:
    """Process a PDF file and extract text from all pages."""
    client = get_client()
    results = []

    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Convert page to JPEG image (smaller size)
        image_base64, mime_type = pdf_page_to_base64(
            page, scale=OCR_DPI_SCALE, jpeg_quality=JPEG_QUALITY
        )

        # Extract text using vision model
        md_text = extract_text_with_vision(client, image_base64, mime_type)

        results.append(
            PageOCR(
                page_number=page_num + 1,  # 1-indexed
                MD_text=md_text,
            )
        )

    doc.close()
    return results


# ============================================================================
# Knowledge Base (Simple In-Memory for now)
# ============================================================================

# Store processed documents in memory (can be replaced with vector DB)
knowledge_base: dict = {
    "documents": {},  # pdf_name -> list of {page_number, content}
}


def add_to_knowledge_base(pdf_name: str, pages: List[PageOCR]):
    """Add processed document to knowledge base."""
    knowledge_base["documents"][pdf_name] = [
        {"page_number": p.page_number, "content": p.MD_text} for p in pages
    ]


def search_knowledge_base(query: str, top_k: int = 3) -> List[Source]:
    """Simple keyword search in knowledge base (replace with vector search)."""
    results = []
    query_lower = query.lower()

    for pdf_name, pages in knowledge_base["documents"].items():
        for page in pages:
            content = page["content"]
            # Simple relevance scoring based on keyword presence
            if any(word in content.lower() for word in query_lower.split()):
                results.append(
                    Source(
                        pdf_name=pdf_name,
                        page_number=page["page_number"],
                        content=content[:1000],  # Limit content length
                    )
                )

    return results[:top_k]


# ============================================================================
# Chat Functions
# ============================================================================

CHAT_SYSTEM_PROMPT = """You are an expert assistant for SOCAR's historical document archive.
You help users find and understand information from historical oil and gas research documents.

When answering questions:
1. Base your answers ONLY on the provided source documents
2. If the information is not in the sources, say so clearly
3. Cite specific pages and documents when possible
4. Provide accurate, technical answers
5. Support answers in Azerbaijani, Russian, or English as needed

Source documents will be provided in the context."""


def generate_chat_response(
    messages: List[ChatMessage], sources: List[Source], model: str = CHAT_MODEL
) -> str:
    """Generate a response using the LLM with retrieved sources."""
    client = get_client()

    # Build context from sources
    context = "## Retrieved Source Documents:\n\n"
    for i, src in enumerate(sources, 1):
        context += f"### Source {i}: {src.pdf_name} (Page {src.page_number})\n"
        context += f"{src.content}\n\n"

    # Build messages for the API
    api_messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT + "\n\n" + context}
    ]

    # Add chat history
    for msg in messages:
        api_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            max_tokens=2000,
            # temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "status": "running",
        "api": "SOCAR Document Processing",
        "version": "1.0.0",
        "endpoints": {
            "ocr": "POST /ocr - Upload PDF for text extraction",
            "chat": "POST /chat - Query the knowledge base",
            "docs": "GET /docs - API documentation",
        },
        "models": {
            "ocr": OCR_MODEL,
            "chat": CHAT_MODEL,
            "embedding": EMBEDDING_MODEL,
        },
    }


@app.post("/ocr", response_model=List[PageOCR])
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    OCR Endpoint - Extract text from PDF documents.

    Accepts a PDF file upload and returns the extracted Markdown text for each page.

    Input: PDF file (multipart/form-data)
    Output: List of {page_number, MD_text} for each page
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        # Read file content
        pdf_bytes = await file.read()

        # Process OCR
        results = process_pdf_ocr(pdf_bytes, file.filename)

        # Add to knowledge base for later querying
        add_to_knowledge_base(file.filename, results)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(messages: List[ChatMessage]):
    """
    LLM Endpoint - Query the knowledge base with chat history.

    Receives chat history and produces an LLM-generated answer along with source references.

    Input: JSON array of {role, content} messages
    Output: {sources: [...], answer: "..."}
    """
    if not messages:
        raise HTTPException(status_code=400, detail="Chat history cannot be empty")

    # Get the latest user message for search
    user_messages = [m for m in messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    latest_query = user_messages[-1].content

    try:
        # Search knowledge base for relevant sources
        sources = search_knowledge_base(latest_query, top_k=3)

        # Generate response
        answer = generate_chat_response(messages, sources)

        return ChatResponse(sources=sources, answer=answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/models")
async def list_models():
    """List available models."""
    return {
        "ocr_model": OCR_MODEL,
        "chat_model": CHAT_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "note": "Set environment variables to change models: OCR_MODEL, CHAT_MODEL, EMBEDDING_MODEL",
    }


@app.get("/knowledge-base/status")
async def knowledge_base_status():
    """Get status of the knowledge base."""
    docs = knowledge_base["documents"]
    return {
        "documents_count": len(docs),
        "documents": [
            {"name": name, "pages": len(pages)} for name, pages in docs.items()
        ],
    }


# ============================================================================
# Run with: uvicorn api:app --reload --host 0.0.0.0 --port 8000
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
