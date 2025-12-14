"""
Response Logger Module - Log API requests and responses to JSON for testing and debugging.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ResponseLogger:
    """Logger for API requests and responses."""
    
    def __init__(self, log_dir: str = "logs/api_responses"):
        """
        Initialize the response logger.
        
        Args:
            log_dir: Directory to store response logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_ocr_request(
        self,
        filename: str,
        page_number: int,
        extracted_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an OCR request and response.
        
        Args:
            filename: PDF filename
            page_number: Page number processed
            extracted_text: Extracted text result
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": "ocr",
            "filename": filename,
            "page_number": page_number,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "text_length": len(extracted_text),
            "metadata": metadata or {}
        }
        
        self._write_log("ocr", filename, log_entry)
    
    def log_chat_request(
        self,
        messages: list,
        answer: str,
        sources: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a chat request and response.
        
        Args:
            messages: Chat history messages
            answer: Generated answer
            sources: Retrieved sources
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": "chat",
            "messages": messages,
            "answer": answer[:500] + "..." if len(answer) > 500 else answer,
            "answer_length": len(answer),
            "sources_count": len(sources),
            "sources": [
                {
                    "pdf_name": src.pdf_name,
                    "page_number": src.page_number,
                    "content_length": len(src.content),
                }
                for src in sources
            ] if sources else [],
            "metadata": metadata or {}
        }
        
        self._write_log("chat", "chat_log", log_entry)
    
    def log_error(
        self,
        endpoint: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error from an API call.
        
        Args:
            endpoint: API endpoint that failed
            error: Error message
            details: Additional error details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "error": error,
            "details": details or {}
        }
        
        self._write_log("errors", endpoint, log_entry)
    
    def _write_log(self, category: str, name: str, log_entry: Dict[str, Any]) -> None:
        """
        Write a log entry to JSON file.
        
        Args:
            category: Log category (ocr, chat, errors)
            name: Log name (filename or endpoint)
            log_entry: Log entry dictionary
        """
        category_dir = self.log_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Clean filename for use in path
        safe_name = "".join(c for c in str(name) if c.isalnum() or c in ".-_")
        log_file = category_dir / f"{safe_name}.jsonl"
        
        try:
            # Append to JSONL file (one JSON object per line)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write response log: {str(e)}")
    
    def get_all_logs(self, category: str = "chat") -> list:
        """
        Read all logs from a category.
        
        Args:
            category: Log category to read
        
        Returns:
            List of log entries
        """
        category_dir = self.log_dir / category
        if not category_dir.exists():
            return []
        
        logs = []
        for log_file in category_dir.glob("*.jsonl"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
            except Exception as e:
                print(f"Warning: Failed to read log file {log_file}: {str(e)}")
        
        return logs


# Global logger instance
_logger: Optional[ResponseLogger] = None


def get_logger() -> ResponseLogger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = ResponseLogger()
    return _logger
