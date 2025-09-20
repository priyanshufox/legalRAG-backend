# app/utils/chunker.py
import re
from typing import List

def simple_text_extractor(filepath: str) -> str:
    # very simple: if .txt just read, if .pdf use pdfplumber
    if filepath.lower().endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.lower().endswith(".pdf"):
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("pdfplumber required for pdf processing")
        text = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text.append(page_text)
        return "\n".join(text)
    else:
        # fallback: read raw
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        # try to not cut mid-sentence: go back to last period within chunk
        if end < len(text):
            last_period = chunk.rfind('. ')
            if last_period != -1 and last_period > max_chars//2:
                chunk = chunk[:last_period+1]
                end = start + len(chunk)
        chunks.append(chunk.strip())
        start = max(end - overlap, end)  # move forward with overlap
    return chunks
