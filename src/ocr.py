"""
OCR Module - Extract text from PDF documents using vision models.

Supports:
- Azerbaijani (Latin script)
- Azerbaijani (Cyrillic script)
- Russian
- Handwritten text
"""

import base64
import io
import asyncio
import logging
import time
from typing import List, Tuple

import fitz  # PyMuPDF
from PIL import Image

from src.config import settings
from src.llm_client import get_client, get_async_client
from src.models import PageOCR
from src.text_corrector import correct_text

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
# OCR Prompt
# ============================================================================

OCR_PROMPT = """You are an expert OCR system specialized in extracting text with MAXIMUM ACCURACY from documents.

Extract ALL text from this document image with extreme precision. The document may contain:
- Azerbaijani text (Latin script)
- Azerbaijani text (Cyrillic script)  
- Russian text
- Technical/scientific terminology (oil and gas engineering)
- Handwritten notes
- Tables, figures, and diagrams
- Images, charts, photographs

Critical Instructions:
1. ACCURACY FIRST: Extract text exactly as it appears - do not correct, reword, or interpret
2. Preserve the original document structure (headings, paragraphs, lists, tables)
3. Output in clean Markdown format
4. For tables, use Markdown table syntax
5. For images, charts, or diagrams: 
   - Describe them with `![Image description](image-reference)` in Markdown
   - Include relevant captions or titles
   - Preserve layout and visual hierarchy
6. For unclear or illegible text, use [unclear] marker
7. Preserve EVERY word, number, date, and technical term EXACTLY as written
8. DO NOT:
   - Paraphrase or reword sentences
   - Add explanations or interpretations
   - Insert corrections or improvements
   - Combine or split sentences
   - Translate text to different language
9. When multiple similar-looking letters exist (like "г" vs "o", "ş" vs "c"), be extremely careful to match the exact character used
10. Output ONLY the extracted text - no preamble, summary, or commentary

Output the extracted Markdown text exactly as it appears in the document:"""


# ============================================================================
# Image Processing
# ============================================================================

def pdf_page_to_base64(
    page: fitz.Page, 
    scale: float = 1.5, 
    jpeg_quality: int = 90
) -> Tuple[str, str]:
    """
    Convert a PDF page to base64-encoded JPEG image.
    
    Args:
        page: PyMuPDF page object
        scale: Resolution scale factor (1.5 = 108 DPI)
        jpeg_quality: JPEG compression quality (0-100)
    
    Returns:
        Tuple of (base64_data, mime_type)
    """
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to JPEG for smaller size
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=jpeg_quality)
    image_bytes = buffer.getvalue()
    
    return base64.b64encode(image_bytes).decode("utf-8"), "image/jpeg"


# ============================================================================
# Vision OCR
# ============================================================================

def extract_text_with_vision(
    image_base64: str, 
    mime_type: str = "image/jpeg",
    model: str | None = None
) -> str:
    """
    Use vision model to extract text from an image with retry logic for rate limiting.
    
    Args:
        image_base64: Base64-encoded image data
        mime_type: Image MIME type
        model: Model to use (defaults to settings.OCR_MODEL)
    
    Returns:
        Extracted text in Markdown format
    """
    if model is None:
        model = settings.OCR_MODEL
    
    client = get_client()
    max_retries = 3
    base_wait_time = 1  # Start with 1 second
    
    for attempt in range(max_retries):
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
                                }
                            }
                        ]
                    }
                ],
                max_completion_tokens=settings.OCR_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            # Check for rate limiting (429) or explicit rate limit errors
            if ("429" in error_str or "RateLimitReached" in error_str or 
                "Exceeded free tier" in error_str or "rate" in error_str.lower()):
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s, 8s...
                    wait_time = base_wait_time * (2 ** attempt)
                    logger.warning(f"Rate limit hit (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit error after {max_retries} retries: {error_str}")
                    return f"[OCR Error: Error code: 429 - {error_str}]"
            else:
                # Non-rate-limit error, return immediately
                return f"[OCR Error: {error_str}]"
    
    return "[OCR Error: Unknown error after retries]"


async def extract_text_with_vision_async(
    image_base64: str, 
    mime_type: str = "image/jpeg",
    model: str | None = None
) -> str:
    """
    Use vision model to extract text from an image with retry logic for rate limiting (asynchronous).
    
    Args:
        image_base64: Base64-encoded image data
        mime_type: Image MIME type
        model: Model to use (defaults to settings.OCR_MODEL)
    
    Returns:
        Extracted text in Markdown format
    """
    if model is None:
        model = settings.OCR_MODEL
    
    client = get_async_client()
    max_retries = 3
    base_wait_time = 1  # Start with 1 second
    
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
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
                                }
                            }
                        ]
                    }
                ],
                max_completion_tokens=settings.OCR_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            # Check for rate limiting (429) or explicit rate limit errors
            if ("429" in error_str or "RateLimitReached" in error_str or 
                "Exceeded free tier" in error_str or "rate" in error_str.lower()):
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s, 8s...
                    wait_time = base_wait_time * (2 ** attempt)
                    logger.warning(f"Rate limit hit (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit error after {max_retries} retries: {error_str}")
                    return f"[OCR Error: Error code: 429 - {error_str}]"
            else:
                # Non-rate-limit error, return immediately
                return f"[OCR Error: {error_str}]"
    
    return "[OCR Error: Unknown error after retries]"


# ============================================================================
# PDF Processing
# ============================================================================

def process_pdf(pdf_bytes: bytes, filename: str) -> List[PageOCR]:
    """
    Process a PDF file and extract text from all pages.
    
    Args:
        pdf_bytes: PDF file content as bytes
        filename: Original filename
    
    Returns:
        List of PageOCR objects with extracted text
    """
    results = []
    
    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Convert page to JPEG image
        image_base64, mime_type = pdf_page_to_base64(
            page, 
            scale=settings.OCR_DPI_SCALE, 
            jpeg_quality=settings.JPEG_QUALITY
        )
        
        # Extract text using vision model
        md_text = extract_text_with_vision(image_base64, mime_type)
        
        # Apply grammar and writing corrections as final layer
        md_text = correct_text(md_text)
        
        results.append(PageOCR(
            page_number=page_num + 1,  # 1-indexed
            MD_text=md_text
        ))
    
    doc.close()
    return results


async def process_pdf_async(pdf_bytes: bytes, filename: str) -> List[PageOCR]:
    """
    Process a PDF file and extract text from all pages in PARALLEL.
    
    Args:
        pdf_bytes: PDF file content as bytes
        filename: Original filename
    
    Returns:
        List of PageOCR objects with extracted text
    """
    logger.info(f"Starting async PDF processing: {filename}")
    
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        logger.info(f"PDF has {page_count} pages")
        
        # Prepare all pages for parallel processing
        page_tasks = []
        for page_num in range(page_count):
            page = doc[page_num]
            logger.debug(f"[Page {page_num + 1}] Converting to image...")
            
            # Convert page to JPEG image
            image_base64, mime_type = pdf_page_to_base64(
                page, 
                scale=settings.OCR_DPI_SCALE, 
                jpeg_quality=settings.JPEG_QUALITY
            )
            logger.debug(f"[Page {page_num + 1}] Image created. Size: {len(image_base64)} bytes")
            
            # Create async task for this page
            task = _process_single_page_async(page_num, image_base64, mime_type)
            page_tasks.append(task)
        
        logger.info(f"Processing {len(page_tasks)} pages in parallel...")
        
        # Process all pages in parallel
        results = await asyncio.gather(*page_tasks, return_exceptions=True)
        
        doc.close()
        logger.debug("PDF document closed")
        
        # Handle results and convert exceptions to error strings
        final_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[Page {idx + 1}] Exception: {str(result)}")
                final_results.append(PageOCR(
                    page_number=idx + 1,
                    MD_text=f"[OCR Error: {str(result)}]"
                ))
            else:
                logger.info(f"[Page {idx + 1}] Successfully processed. Text length: {len(result.MD_text)}")
                final_results.append(result)
        
        logger.info(f"Async PDF processing complete for {filename}")
        return final_results
    
    except Exception as e:
        logger.error(f"Fatal error in async PDF processing: {str(e)}", exc_info=True)
        raise


async def _process_single_page_async(
    page_num: int,
    image_base64: str,
    mime_type: str
) -> PageOCR:
    """
    Process a single PDF page asynchronously.
    
    Args:
        page_num: Page number (0-indexed)
        image_base64: Base64-encoded page image
        mime_type: Image MIME type
    
    Returns:
        PageOCR object with extracted text
    """
    try:
        logger.debug(f"[Page {page_num + 1}] Starting OCR extraction...")
        
        # Extract text using vision model
        md_text = await extract_text_with_vision_async(image_base64, mime_type)
        logger.debug(f"[Page {page_num + 1}] OCR extraction complete. Text length: {len(md_text)}")
        
        if not md_text or md_text.startswith("[OCR Error"):
            logger.warning(f"[Page {page_num + 1}] OCR returned error or empty: {md_text[:100]}")
            return PageOCR(
                page_number=page_num + 1,
                MD_text=md_text
            )
        
        logger.debug(f"[Page {page_num + 1}] Applying text correction...")
        
        # Apply grammar and writing corrections as final layer
        try:
            corrected_text = correct_text(md_text)
            if corrected_text and len(corrected_text.strip()) > 0:
                md_text = corrected_text
                logger.debug(f"[Page {page_num + 1}] Text correction complete. Final length: {len(md_text)}")
            else:
                logger.warning(f"[Page {page_num + 1}] Text correction returned empty, keeping original OCR text")
        except Exception as e:
            logger.error(f"[Page {page_num + 1}] Text correction failed: {str(e)}")
            # Continue with uncorrected text
        
        logger.debug(f"[Page {page_num + 1}] Final text length: {len(md_text)}")
        
        return PageOCR(
            page_number=page_num + 1,  # 1-indexed
            MD_text=md_text
        )
    except Exception as e:
        logger.error(f"[Page {page_num + 1}] Unexpected error: {str(e)}", exc_info=True)
        return PageOCR(
            page_number=page_num + 1,
            MD_text=f"[OCR Error: {str(e)}]"
        )


def process_pdf_file(pdf_path: str) -> List[PageOCR]:
    """
    Process a PDF file from disk.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of PageOCR objects
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    filename = pdf_path.split("/")[-1]
    return process_pdf(pdf_bytes, filename)
