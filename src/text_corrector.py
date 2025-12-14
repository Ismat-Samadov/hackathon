"""
Text Corrector Module - Fix grammar and writing issues in OCR output using LLM.

Applies a final layer of text correction to:
- Fix spelling errors from OCR
- Correct grammar issues
- Preserve original script (Cyrillic, Latin, etc.)
- Maintain technical terminology accuracy
- Keep document structure and formatting
"""

import logging
from src.config import settings
from src.llm_client import get_client

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
# Text Correction Prompt
# ============================================================================

CORRECTION_PROMPT = """You are an expert text editor specializing in correcting OCR output for Azerbaijani and Russian documents.

Your task is to fix OCR errors in the extracted text while maintaining accuracy:

CORRECTIONS TO APPLY:
1. Fix obvious OCR character confusions:
   - Cyrillic 'г' (g) vs Latin 'r' vs '9'
   - Cyrillic 'о' (o) vs Latin 'o' vs '0' (zero)
   - Cyrillic 'с' (s) vs Latin 'c' vs Latin 's'
   - 'l' (L) vs 'I' (i) vs '1' (one)
   - 'ş' vs 'c' vs 'q'
   - 'ə' vs 'a' vs 'α'

2. Fix Azerbaijani/Russian spelling errors (common OCR mistakes):
   - "çöküntütoplanma" vs "çöküntü toplanma" (compound word spacing)
   - "seçilir" vs "səciyyələnir" (homophone confusions)
   - "girin" vs "şirin" (ş vs g confusion)
   - "cəmlənir" vs "görünür" vs "cəmlənir" (semantic restoration)
   
3. Correct word boundary issues where OCR merged/split words incorrectly
4. Fix punctuation and spacing issues
5. Preserve the original script (Cyrillic stays Cyrillic, Latin stays Latin)
6. Keep technical terminology and domain-specific terms
7. Maintain document structure (Markdown, lists, tables)
8. Keep [unclear] markers as-is
9. Do NOT add, remove, or reinterpret content - only fix character-level errors
10. Do NOT transliterate between scripts

CONTEXT CLUES FOR CORRECTIONS:
- In oil/gas engineering documents, look for domain-specific terms
- Use linguistic patterns to identify word boundaries
- Apply morphological rules for Azerbaijani/Russian

Return ONLY the corrected text with no commentary or explanations."""


# ============================================================================
# Text Correction Functions
# ============================================================================

def correct_text(text: str, model: str | None = None) -> str:
    """
    Correct grammar and writing issues in extracted text using LLM.
    
    Args:
        text: OCR-extracted text to correct
        model: Model to use (defaults to settings.CHAT_MODEL)
    
    Returns:
        Grammar-corrected text
    """
    if model is None:
        model = settings.CHAT_MODEL
    
    if not text or not text.strip():
        logger.debug("Skipping correction: text is empty")
        return text
    
    logger.debug(f"Starting text correction with model {model}. Text length: {len(text)}")
    
    client = get_client()
    
    try:
        # Use max_completion_tokens (supported by all modern models)
        logger.debug(f"Sending correction request with max_completion_tokens={min(len(text) + 500, 4000)}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": CORRECTION_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Here is the text to correct:\n\n{text}"
                }
            ],
            max_completion_tokens=min(len(text) + 500, 4000),  # Cap at 4000 tokens
        )
        
        logger.debug(f"Response received. Choices count: {len(response.choices)}")
        logger.debug(f"Response.choices[0].message: {response.choices[0].message}")
        logger.debug(f"Response.choices[0].message.content (raw): '{response.choices[0].message.content}'")
        
        corrected = response.choices[0].message.content
        if corrected is None:
            logger.warning("Response content is None, returning original text")
            return text
        
        corrected = corrected.strip()
        logger.debug(f"Text correction successful. Output length: {len(corrected)}")
        
        if len(corrected) == 0:
            logger.warning("Response content is empty string, returning original text")
            return text
        
        return corrected
        
    except Exception as e:
        # Log the error properly instead of silent failure
        logger.error(f"Text correction failed: {str(e)}", exc_info=True)
        logger.warning(f"Returning original uncorrected text (length: {len(text)})")
        return text
