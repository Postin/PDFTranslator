from PyPDF2 import PdfReader
from typing import List


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extracts text from each page of a digital/text-based PDF.

    Args:
        pdf_path (str): Path to the input PDF.

    Returns:
        List[str]: List of text strings, one per page.
    """
    pages = []
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            cleaned_text = text.strip() if text else ""
            pages.append(cleaned_text)
    except Exception as e:
        print(f"[ERROR] Failed to extract text from '{pdf_path}': {e}")

    return pages