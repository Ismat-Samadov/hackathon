"""
Ingest all PDF documents from hackathon_data folder into Pinecone.

This script:
1. Processes all PDFs in hackathon_data/
2. Extracts text using OCR
3. Stores in Pinecone with embeddings and metadata (pdf_name, page_number, content chunks)
"""

import asyncio
import logging
from pathlib import Path
from src.ocr import process_pdf_async
from src.knowledge_base import knowledge_base

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def ingest_all_pdfs():
    """Ingest all PDFs from hackathon_data folder."""

    # Find all PDFs
    data_dir = Path("hackathon_data")
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {data_dir}")
        return

    logger.info("=" * 70)
    logger.info(f"Found {len(pdf_files)} PDF files to ingest")
    logger.info("=" * 70)

    # Clear existing index (optional - comment out to append instead)
    logger.info("\nClearing Pinecone index...")
    knowledge_base.clear()
    logger.info("✓ Index cleared\n")

    # Process each PDF
    for i, pdf_path in enumerate(sorted(pdf_files), 1):
        logger.info(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
        logger.info("-" * 70)

        try:
            # Read PDF
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            # Process with OCR
            logger.info("  Running OCR...")
            pages = await process_pdf_async(pdf_bytes, pdf_path.name)
            logger.info(f"  ✓ Extracted {len(pages)} pages")

            # Add to Pinecone
            logger.info("  Indexing to Pinecone...")
            knowledge_base.add_document(pdf_path.name, pages)
            logger.info(f"  ✓ Indexed with embeddings and metadata")

        except Exception as e:
            logger.error(f"  ✗ Failed to process {pdf_path.name}: {e}")
            continue

    # Final status
    logger.info("\n" + "=" * 70)
    logger.info("Ingestion Complete!")
    logger.info("=" * 70)

    status = knowledge_base.get_status()
    logger.info(f"Total vectors in Pinecone: {status['total_vectors']}")
    logger.info(f"Index name: {status['index_name']}")
    logger.info(f"Dimension: {status.get('dimension', 'N/A')}")

    # Test search
    logger.info("\n" + "=" * 70)
    logger.info("Testing Search with Content Retrieval")
    logger.info("=" * 70)

    test_queries = ["Azərbaycanda neft", "oil and gas", "temperature pressure"]

    for query in test_queries:
        logger.info(f"\nQuery: '{query}'")
        results = knowledge_base.search(query, top_k=3)

        for i, src in enumerate(results, 1):
            content_preview = src.content[:100] if src.content else "[EMPTY]"
            logger.info(f"  {i}. {src.pdf_name} (Page {src.page_number})")
            logger.info(
                f"     Content ({len(src.content)} chars): {content_preview}..."
            )


if __name__ == "__main__":
    asyncio.run(ingest_all_pdfs())
