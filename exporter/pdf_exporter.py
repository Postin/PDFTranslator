import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def create_bilingual_pdf(
    pages: list,
    output_path: str,
    source_lang: str,
    target_lang: str,
    font_path: str = None,
    font_name: str = "DejaVuSans",
    font_size: int = 11,
    margin_cm: float = 2.5
):
    """
    Create a PDF document with original and translated text for each page.
    Sequential layout: original text first, then translation below.
    
    Args:
        pages: List of dicts with {"original": str, "translated": str, "page_num": int}
        output_path: Output PDF file path
        source_lang: Source language name (for headers)
        target_lang: Target language name (for headers)
        font_path: Path to TTF font file (for Unicode support)
        font_name: Name to register the font as
        font_size: Base font size
        margin_cm: Page margin in centimeters
    """
    # Find font file
    if font_path is None:
        # Look for font in common locations
        possible_paths = [
            "fonts/DejaVuSans.ttf",
            os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        ]
        for path in possible_paths:
            if os.path.exists(path):
                font_path = path
                break
    
    # Register font if available
    if font_path and os.path.exists(font_path):
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        # Fallback to Helvetica (no Unicode support)
        font_name = "Helvetica"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = margin_cm * cm
    usable_width = width - 2 * margin
    line_height = font_size * 1.4
    header_size = font_size + 4
    
    for page_data in pages:
        page_num = page_data["page_num"]
        original = page_data.get("original", "")
        translated = page_data.get("translated", "")
        
        y = height - margin
        
        # Page header
        c.setFont(font_name, header_size + 2)
        c.drawCentredString(width / 2, y, f"Page {page_num}")
        y -= line_height * 2
        
        # Original section header
        c.setFont(font_name, header_size)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(margin, y, f"Original ({source_lang})")
        c.setFillColorRGB(0, 0, 0)
        y -= line_height * 1.5
        
        # Original text
        c.setFont(font_name, font_size)
        y = _draw_text_block(c, original, margin, y, usable_width, line_height, 
                             font_name, font_size, margin, height)
        
        # Separator
        y -= line_height
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.line(margin, y, width - margin, y)
        y -= line_height * 1.5
        
        # Check if we need a new page
        if y < margin + line_height * 5:
            c.showPage()
            y = height - margin
        
        # Translation section header
        c.setFont(font_name, header_size)
        c.setFillColorRGB(0, 0.4, 0.6)
        c.drawString(margin, y, f"Translation ({target_lang})")
        c.setFillColorRGB(0, 0, 0)
        y -= line_height * 1.5
        
        # Translated text
        c.setFont(font_name, font_size)
        y = _draw_text_block(c, translated, margin, y, usable_width, line_height,
                             font_name, font_size, margin, height)
        
        # Page break
        c.showPage()
    
    c.save()
    print(f"Bilingual PDF saved to: {output_path}")


def _draw_text_block(canvas_obj, text, x, y, max_width, line_height, 
                     font_name, font_size, margin, page_height):
    """
    Draw a block of text with word wrapping and page breaks.
    
    Returns:
        float: The y position after drawing
    """
    paragraphs = text.split("\n")
    
    for para in paragraphs:
        if not para.strip():
            y -= line_height * 0.5
            continue
        
        # Word wrap
        wrapped_lines = simpleSplit(para.strip(), font_name, font_size, max_width)
        
        for line in wrapped_lines:
            # Check for page break
            if y < margin + line_height:
                canvas_obj.showPage()
                canvas_obj.setFont(font_name, font_size)
                y = page_height - margin
            
            canvas_obj.drawString(x, y, line)
            y -= line_height
    
    return y
