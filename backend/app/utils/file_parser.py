"""
File Parser
===========
Extracts raw text from PDF and DOCX files using pdfplumber and python-docx.
"""

import os

import pdfplumber
from docx import Document

from app.core.exceptions import FileProcessingException


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        FileProcessingException: If parsing fails.
    """
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        raise FileProcessingException(f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Concatenated text from all paragraphs.

    Raises:
        FileProcessingException: If parsing fails.
    """
    try:
        doc = Document(file_path)
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(text_parts)
    except Exception as e:
        raise FileProcessingException(f"Failed to parse DOCX: {str(e)}")


def extract_text(file_path: str) -> str:
    """
    Auto-detect file type and extract text.

    Args:
        file_path: Path to a PDF or DOCX file.

    Returns:
        Extracted text content.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        raise FileProcessingException(f"Unsupported file type: {ext}")
