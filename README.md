# SOCAR Historical Document Processing System

A complete solution for transforming historical handwritten and printed documents into an interactive, searchable knowledge base accessible through an intelligent chat agent interface.

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
│                     Knowledge Base                              │
│              (In-memory / Vector DB ready)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Azure AI Foundry                              │
│                                                                 │
│  OCR:       Llama-4-Maverick-17B-128E-Instruct-FP8 (Vision)    │
│  Chat:      Llama-4-Maverick-17B-128E-Instruct-FP8             │
│  Embedding: Cohere-embed-v3-multilingual                        │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
samir_hackathon/
├── main.py                 # Entry point - starts API server
├── api.py                  # Legacy API (kept for compatibility)
├── pyproject.toml          # Project dependencies
├── .env                    # Environment variables (API keys)
├── README.md               # This file
│
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── models.py           # Pydantic models (request/response)
│   ├── llm_client.py       # Azure OpenAI client
│   ├── ocr.py              # OCR processing module
│   ├── chat.py             # Chat/RAG module
│   ├── knowledge_base.py   # Document storage & retrieval
│   └── api.py              # FastAPI application
│
├── scripts/                # Utility scripts
│   ├── test_api.py         # API testing script
│   └── test_models.py      # Model testing script
│
├── hackathon_data/         # Sample PDF documents
│   └── *.pdf
│
└── tests/                  # Unit tests (TODO)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

```bash
# Copy .env.example to .env and set your API keys
cp .env.example .env

# Required variables:
BASE_URL=https://llmapihackathon.services.ai.azure.com/
API_KEY=your_api_key_here
```

### 3. Start the Server

```bash
# Using the main entry point
python main.py

# Or with uvicorn directly
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Or using uv
uv run python main.py
```

### 4. Access the API

- **API Root**: http://localhost:8000/
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### OCR Endpoint

**POST /ocr**

Extract text from PDF documents.

```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf"
```

**Response:**
```json
[
  {
    "page_number": 1,
    "MD_text": "## Title\n\nExtracted markdown text..."
  },
  {
    "page_number": 2,
    "MD_text": "More extracted text..."
  }
]
```

### Chat Endpoint

**POST /chat**

Query the knowledge base with conversation history.

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "What is this document about?"}]'
```

**Response:**
```json
{
  "sources": [
    {
      "pdf_name": "document.pdf",
      "page_number": 1,
      "content": "Relevant extracted text..."
    }
  ],
  "answer": "Based on the documents, this is about..."
}
```

## 🛠️ Technology Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| **OCR** | Llama-4-Maverick (Vision) | Open source, multimodal, excellent quality |
| **Chat** | Llama-4-Maverick | Open source, fast, multilingual |
| **Embeddings** | Cohere-embed-v3-multilingual | Best for Azerbaijani text |
| **API** | FastAPI | Modern, fast, auto-documentation |
| **PDF Processing** | PyMuPDF | Fast, reliable PDF handling |

## 🎯 Supported Document Types

| Type | Script/Language | Difficulty | Status |
|------|-----------------|------------|--------|
| PDF Aze Print | Azerbaijani (Latin) | Easy | ✅ Supported |
| PDF Cyr Print | Azerbaijani (Cyrillic) / Russian | Medium | ✅ Supported |
| PDF Aze Hand | Azerbaijani (Handwritten) | Hard | ✅ Supported |

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# Azure AI Foundry
BASE_URL=https://llmapihackathon.services.ai.azure.com/
API_KEY=your_api_key

# Models (Open Source preferred)
OCR_MODEL=Llama-4-Maverick-17B-128E-Instruct-FP8
CHAT_MODEL=Llama-4-Maverick-17B-128E-Instruct-FP8
EMBEDDING_MODEL=Cohere-embed-v3-multilingual

# OCR Settings
OCR_DPI_SCALE=1.5
OCR_MAX_TOKENS=4000
JPEG_QUALITY=90

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 Evaluation Criteria

### OCR Benchmark (50%)
- CER (Character Error Rate)
- WER (Word Error Rate)

### Chatbot Benchmark (30%)
- Answer accuracy
- Citation relevance
- Citation order

### Architecture (20%)
- Open source preference ✅
- Technical quality
- Innovation

## 🔧 Development

```bash
# Run tests
pytest tests/

# Format code
black src/
ruff src/

# Type checking
mypy src/
```

## 📝 License

MIT License - SOCAR Hackathon 2024

## 👥 Team

- Team Member 1
- Team Member 2
- Team Member 3



