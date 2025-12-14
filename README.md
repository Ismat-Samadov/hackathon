# SOCAR Historical Document Processing System

Production-ready RAG system for processing and querying SOCAR's historical oil & gas documents. Transforms scanned PDFs into an interactive, searchable knowledge base with intelligent chat interface.

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your Azure AI Foundry and Pinecone credentials

# 3. Start the API server
uv run uvicorn src.api:app --host 0.0.0.0 --port 8000

# 4. Access Swagger UI
open http://localhost:8000/docs
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (REST API / Swagger UI)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                         FastAPI Server                          │
│                    POST /ocr    POST /chat                      │
└───────────┬─────────────────────────────────┬───────────────────┘
            │                                 │
┌───────────▼───────────┐       ┌─────────────▼─────────────┐
│     OCR Module        │       │      Chat Module          │
│  (Vision LLM-based)   │       │  (RAG + LLM Generation)   │
│                       │       │                           │
│  • PDF → Image        │       │  • Query Processing       │
│  • Image → Text       │       │  • Context Retrieval      │
│  • Markdown Output    │       │  • Response Generation    │
└───────────┬───────────┘       └─────────────┬─────────────┘
            │                                 │
            └─────────────┬───────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                  Knowledge Base (RAG)                           │
│            Pinecone Vector Database + Embeddings                │
│                                                                 │
│  • Semantic Search (Vector Similarity)                          │
│  • Chunk-based Indexing                                         │
│  • Local BGE Embeddings (Open-source, 1024 dim)                 │
│  • Cloud-hosted Serverless (AWS us-east-1)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Azure AI Foundry                              │
│                                                                 │
│  OCR:       Llama-4-Maverick-17B-128E-Instruct-FP8 (Vision)    │
│  Chat:      Llama-4-Maverick-17B-128E-Instruct-FP8             │
│  Embedding: BAAI/bge-large-en-v1.5 (Local, 1024 dim)           │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 RAG (Retrieval Augmented Generation) Implementation

### Overview

Our RAG system uses **Pinecone vector database** for semantic search, enabling accurate retrieval of relevant document chunks based on query meaning rather than just keywords.

### RAG Pipeline

```
User Query → Embedding → Vector Search → Relevant Chunks → LLM → Contextualized Answer
```

1. **Query Embedding**: Convert user question to vector using Cohere multilingual embeddings
2. **Vector Search**: Find semantically similar document chunks in Pinecone
3. **Context Building**: Construct prompt with retrieved sources
4. **Answer Generation**: LLM generates answer citing specific sources
5. **Response**: Return answer + source citations (pdf_name, page_number, content)

### Key Features

✅ **Semantic Search**: Understands meaning, not just keywords  
✅ **Open-Source Embeddings**: BAAI/bge-large-en-v1.5 (local, deployable, 1024 dim)  
✅ **Chunk-based Indexing**: Optimal context size (1000 chars, 200 overlap)  
✅ **Cloud Vector DB**: Pinecone serverless (AWS us-east-1)  
✅ **Source Citations**: Full traceability to original PDFs  
✅ **Conversation History**: Context-aware multi-turn conversations  

### Configuration

```bash
# Pinecone Vector Database (Required)
PINECONE_API_KEY=pcsk_2aNboE_GqcDREwMDyGKQkg6paRUG6tFJwK1CtyQwZ5dgmFCGVUmyVK1bA167LNNMkdYLY3
PINECONE_INDEX_NAME=hackathon
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Embedding Model (1024 dimensions)
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Chunking Strategy
CHUNK_SIZE=1000          # Characters per chunk
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RESULTS=5          # Number of chunks to retrieve
```

### How It Works

#### 1. Document Indexing (POST /ocr)

When a PDF is processed:
1. OCR extracts text from each page
2. Text is split into overlapping chunks (1000 chars, 200 overlap)
3. Each chunk is embedded locally using BAAI/bge-large-en-v1.5 (1024 dimensions)
4. Vectors are stored in Pinecone with metadata (pdf_name, page_number, content)

```python
# Automatic indexing after OCR
results = await process_pdf_async(pdf_bytes, filename)
knowledge_base.add_document(filename, results)  # → Pinecone
```

#### 2. Semantic Search (POST /chat)

When a user asks a question:
1. Query is embedded locally using the same BGE model (1024 dimensions)
2. Pinecone performs cosine similarity search
3. Top-K most relevant chunks are retrieved
4. Chunks are formatted as sources with citations

```python
# Vector search
sources = knowledge_base.search(query, top_k=5)
# Returns: List[Source(pdf_name, page_number, content)]
```

#### 3. Answer Generation

Retrieved sources are injected into the LLM prompt:
1. System prompt defines the assistant's role
2. Retrieved sources are formatted as context
3. Conversation history is included
4. LLM generates cited answer

### Response Format

```json
{
  "sources": [
    {
      "pdf_name": "Abseron-KurMQAltHorizontları.pdf",
      "page_number": 3,
      "content": "Temperature ranges: 150-200°C, Pressure: 300-400 bar..."
    },
    {
      "pdf_name": "PirallahıTektonostratigrafiyası.pdf",
      "page_number": 7,
      "content": "Geological formations contain significant reserves..."
    }
  ],
  "answer": "Based on the technical specifications (Abseron document, page 3), the temperature ranges are 150-200°C with pressure at 300-400 bar. The geological surveys (Pirallahı document, page 7) indicate significant hydrocarbon reserves in these formations."
}
```

### Testing RAG

```bash
# Run RAG test suite
python test_rag.py

# Tests:
# ✓ Pinecone connection
# ✓ Document indexing with embeddings
# ✓ Vector semantic search
# ✓ RAG-based chat responses
# ✓ Conversation history handling
```

### Architecture Decision: Why Pinecone?

| Feature | Pinecone | FAISS | In-Memory |
|---------|----------|-------|-----------|
| **Scalability** | ✅ Serverless | ⚠️ Local only | ❌ RAM limited |
| **Persistence** | ✅ Cloud storage | ⚠️ File-based | ❌ Ephemeral |
| **Performance** | ✅ Optimized | ✅ Fast | ✅ Fastest |
| **Setup** | ✅ Simple API | ⚠️ Complex | ✅ Zero config |
| **Multi-tenant** | ✅ Native | ❌ Manual | ❌ Not suitable |
| **Cost** | ⚠️ Paid (free tier) | ✅ Free | ✅ Free |

**Decision**: Pinecone for production-quality semantic search with cloud scalability.

## 📁 Project Structure

```
samir_hackathon/
├── main.py                 # Entry point - starts API server
├── ingest_pdfs.py          # Bulk PDF ingestion script
├── pyproject.toml          # Project dependencies (uv)
├── .env                    # Environment variables (API keys)
├── .env.example            # Environment template
├── README.md               # This file
│
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── api.py              # FastAPI application & endpoints
│   ├── config.py           # Configuration (env variables)
│   ├── models.py           # Pydantic schemas
│   ├── llm_client.py       # Azure AI Foundry client
│   ├── ocr.py              # OCR processing (vision LLM)
│   ├── chat.py             # RAG chat handler
│   ├── knowledge_base.py   # Pinecone vector database
│   ├── text_corrector.py   # OCR text correction
│   └── response_logger.py  # API response logging
│
├── scripts/                # Deployment scripts
│   ├── setup-nginx.sh      # Nginx reverse proxy setup
│   └── start-api.sh        # Production startup script
│
├── hackathon_data/         # PDF document collection (28 files)
│   └── *.pdf               # SOCAR historical documents
│
└── logs/                   # API response logs
    └── api_responses/
        ├── ocr/            # OCR processing logs
        └── chat/           # Chat response logs
```

## 🚀 Usage

### 1. Start API Server

```bash
# Development mode
uv run python main.py

# Production mode (with nginx)
bash scripts/start-api.sh
```

### 2. Ingest Documents

```bash
# Process all PDFs in hackathon_data/
uv run python ingest_pdfs.py

# This will:
# 1. OCR each PDF page
# 2. Extract and clean text
# 3. Chunk text (1000 chars, 200 overlap)
# 4. Generate embeddings (BAAI/bge-large-en-v1.5)
# 5. Index in Pinecone with metadata
```

### 3. Access API

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## 📚 API Endpoints

### OCR Endpoint

**POST /ocr**

Extract text from PDF documents.

```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf"
```

### POST /ocr

Process PDF documents and extract text via OCR.

**Request:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf"
```

**Response:**
```json
[
  {
    "page_number": 1,
    "MD_text": "## Document Title\n\nExtracted markdown text from page 1..."
  },
  {
    "page_number": 2,
    "MD_text": "Continuation of text from page 2..."
  }
]
```

### POST /chat

Query the RAG system with conversation history. Returns answer with source citations.

**Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Qərbi Abşeron yatağında suvurma tədbirləri haqqında məlumat ver"}
    ]
  }'
```

**Response:**
```json
{
  "sources": [
    {
      "pdf_name": "Qərbi Abşeron Yatağı Modelləşdirmə.pdf",
      "page_number": 15,
      "content": "23.02.1986-cı ildən venoz layda suvurma tədbirləri tətbiq edilmişdir..."
    }
  ],
  "answer": "Qərbi Abşeron yatağında 1986-cı il fevral ayından suvurma tədbirləri başladılmışdır..."
}
```

## 🛠️ Technology Stack

| Component | Technology | Details |
|-----------|------------|---------|
| **OCR** | Llama-4-Maverick-17B (Vision) | Multimodal LLM, handles Cyrillic/Latin/Handwritten |
| **Chat** | Llama-4-Maverick-17B | Fast inference, Azerbaijani language support |
| **Embeddings** | BAAI/bge-large-en-v1.5 (Local) | Open-source, 1024 dim, sentence-transformers |
| **Vector DB** | Pinecone Serverless | Cloud-native, AWS us-east-1, production-ready |
| **API Framework** | FastAPI | Auto-documentation, async support, type safety |
| **PDF Processing** | PyMuPDF (fitz) | Fast rendering, image extraction |
| **Python Runtime** | Python 3.12 + uv | Modern dependency management |

## 🎯 Supported Document Types

| Type | Script/Language | Characteristics | Status |
|------|-----------------|-----------------|--------|
| **PDF Aze Print** | Azerbaijani (Latin) | Printed technical documents | ✅ Excellent |
| **PDF Cyr Print** | Azerbaijani/Russian (Cyrillic) | Historical documents | ✅ Excellent |
| **PDF Aze Hand** | Azerbaijani (Handwritten) | Handwritten notes, forms | ✅ Good |

## ⚙️ Configuration

Key environment variables (`.env`):

```bash
# Azure AI Foundry API
BASE_URL=https://llmapihackathon.services.ai.azure.com/
API_KEY=your_azure_api_key_here

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=hackathon
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Models
OCR_MODEL=Llama-4-Maverick-17B-128E-Instruct-FP8
CHAT_MODEL=Llama-4-Maverick-17B-128E-Instruct-FP8
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# RAG Configuration
CHUNK_SIZE=1000              # Text chunk size (characters)
CHUNK_OVERLAP=200            # Overlap between chunks
TOP_K_RESULTS=5              # Number of sources to retrieve

# OCR Settings
OCR_DPI_SCALE=1.5           # Image resolution multiplier
OCR_MAX_TOKENS=4000
JPEG_QUALITY=90

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 Hackathon Evaluation Criteria

### 1. OCR Benchmark (50%)
- **CER (Character Error Rate)**: Measures character-level accuracy
- **WER (Word Error Rate)**: Measures word-level accuracy
- **Approach**: Vision LLM (Llama-4-Maverick) with optimized prompts

### 2. Chatbot/RAG Benchmark (30%)
- **Citation Relevance**: Accuracy of retrieved sources
- **Citation Order**: Ranking quality of sources
- **Answer Accuracy**: Correctness compared to ground truth
- **Approach**: Pinecone vector DB + local BGE embeddings + RAG pipeline

### 3. Architecture Quality (20%)
- ✅ **Open Source Preference**: BAAI/bge embeddings (local, deployable)
- ✅ **Production Ready**: Pinecone serverless, FastAPI, proper error handling
- ✅ **Scalability**: Cloud-native vector DB, efficient chunking
- ✅ **Code Quality**: Modular design, type hints, documentation

## 🚀 Deployment

### Production Setup

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.12 nginx

# 2. Setup application
git clone <repository>
cd samir_hackathon
uv sync

# 3. Configure nginx reverse proxy
sudo bash scripts/setup-nginx.sh

# 4. Start API server
bash scripts/start-api.sh

# API will be available at http://your-domain.com
```

## 📝 License

MIT License - Built for SOCAR Historical Document Processing Hackathon 2025

## 👥 Team

Developed by Team BeatByte for SOCAR Hackathon

---

**Built with ❤️ using FastAPI, Pinecone, and Azure AI Foundry**
ruff src/

# Type checking
mypy src/
```

## 📝 License

MIT License - SOCAR Hackathon 2025

## 👥 Team

- Team Member 1 Samir Mehdiyev
- Team Member 2 Ismat Samadov
- Team Member 3 Ulvi Bashirov



