import os
from typing import List, Union
from PIL import Image
import fitz  # PyMuPDF


def analyze_pdf_page(page: fitz.Page, min_text_coverage: float = 0.8) -> bool:
    """
    Determine if a PDF page has extractable text or is scanned/image-based.
    
    Args:
        page: PyMuPDF page object
        min_text_coverage: Minimum ratio of text blocks to consider page as text-based
        
    Returns:
        True if page is text-based, False if scanned/image-based
    """
    text = page.get_text().strip()
    
    # If there's substantial text, consider it text-based
    if len(text) > 100:
        # Check if there are images that might indicate a scanned page
        # Use full=True to get complete image info needed for get_image_bbox
        image_list = page.get_images(full=True)
        
        # If single large image covers most of the page, it's likely scanned
        if len(image_list) == 1:
            try:
                img_rect = page.get_image_bbox(image_list[0])
                if img_rect:
                    page_area = page.rect.width * page.rect.height
                    img_area = img_rect.width * img_rect.height
                    if img_area / page_area > 0.7:
                        return False
            except (ValueError, Exception):
                # If we can't get image bbox, assume it's text-based if text exists
                pass
        
        return True
    
    return False


def extract_text_from_page(page: fitz.Page) -> str:
    """Extract text content from a PDF page."""
    return page.get_text().strip()


def render_page_to_image(page: fitz.Page, dpi: int = 200) -> Image.Image:
    """Render a PDF page to a PIL Image."""
    zoom = dpi / 72  # 72 is the default PDF DPI
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)
    
    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def load_pdf(
    pdf_path: str,
    cache_dir: str = "translation_cache/images",
    dpi: int = 200
) -> List[dict]:
    """
    Load a PDF and extract content from each page.
    Automatically detects if pages are text-based or scanned.
    
    Args:
        pdf_path: Path to the PDF file
        cache_dir: Directory to cache rendered images
        dpi: Resolution for rendering scanned pages
        
    Returns:
        List of dicts with structure:
        {
            "page_num": int,
            "content": str | Image.Image,
            "type": "text" | "image"
        }
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    os.makedirs(cache_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    pages = []
    
    print(f"Analyzing {len(doc)} pages...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_data = {"page_num": page_num + 1}
        
        if analyze_pdf_page(page):
            # Text-based page - extract text directly
            page_data["content"] = extract_text_from_page(page)
            page_data["type"] = "text"
        else:
            # Scanned/image page - render to image
            cache_path = os.path.join(cache_dir, f"page_{page_num + 1:03d}.png")
            
            if os.path.exists(cache_path):
                # Load from cache
                page_data["content"] = Image.open(cache_path)
            else:
                # Render and cache
                img = render_page_to_image(page, dpi=dpi)
                img.save(cache_path, "PNG")
                page_data["content"] = img
            
            page_data["type"] = "image"
        
        pages.append(page_data)
    
    doc.close()
    
    # Summary
    text_pages = sum(1 for p in pages if p["type"] == "text")
    image_pages = sum(1 for p in pages if p["type"] == "image")
    print(f"Loaded {len(pages)} pages: {text_pages} text-based, {image_pages} scanned/image")
    
    return pages
