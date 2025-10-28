import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text content from a PDF file.

    Args:
        pdf_path (str): The file path of the PDF to extract from.

    Returns:
        str: Extracted text combined from all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        Exception: For any other error during extraction.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")

    return text
