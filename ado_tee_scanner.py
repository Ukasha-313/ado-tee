"""
ADO-TEE Scanner Module
Handles text extraction from .docx, .xlsx, .pdf, and .txt files,
and calculates SHA-256 hashes for duplicate tracking.
"""

import hashlib
from pathlib import Path
import docx
import openpyxl
import pypdf

# Supported document extensions
TARGET_EXTENSIONS = {".docx", ".xlsx", ".pdf", ".txt", ".md", ".csv"}

def calculate_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file for duplicate detection."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def extract_text(file_path: Path) -> str:
    """Extract readable text from PDF, DOCX, XLSX, TXT, or CSV files."""
    ext = file_path.suffix.lower()
    text = ""
    try:
        if ext in {".txt", ".md", ".csv"}:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        elif ext == ".docx":
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif ext == ".xlsx":
            wb = openpyxl.load_workbook(file_path, data_only=True)
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for row in ws.iter_rows(values_only=True):
                    row_text = " ".join([str(cell) for cell in row if cell is not None])
                    if row_text.strip():
                        text += row_text + "\n"
        elif ext == ".pdf":
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as error:
        print(f"[ERROR] Failed to extract text from {file_path.name}: {error}")
    
    return text