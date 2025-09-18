from PyPDF2 import PdfReader


def is_scanned_pdf(pdf_path: str, min_text_threshold: int = 20) -> bool:
    """
    Returns True if the PDF is likely scanned (image-based), False if it's a digital/text PDF.
    """
    try:
        reader = PdfReader(pdf_path)
        text_chars = 0
        max_pages = min(3, len(reader.pages))

        for i in range(max_pages):
            text = reader.pages[i].extract_text()
            if text:
                text_chars += len(text.strip())

        return text_chars < min_text_threshold
    except Exception as e:
        print(f"[Warning] Could not analyze PDF: {e}")
        return True  # Default to scanned if error occurs