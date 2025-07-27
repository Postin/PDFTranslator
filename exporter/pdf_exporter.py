from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import re
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Register DejaVu Sans
pdfmetrics.registerFont(TTFont("DejaVuSans", "../fonts/DejaVuSans.ttf"))


def export_text_to_pdf(
    input_txt_path: str,
    output_pdf_path: str,
    font_path: str = "fonts/DejaVuSans.ttf",
    font_name: str = "DejaVuSans",
    font_size: int = 11,
    margin_cm: float = 2.5
):

    if not os.path.exists(input_txt_path):
        print(f"❌ File not found: {input_txt_path}")
        return

    with open(input_txt_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Match page header + content
    matches = re.findall(
        r"-{3,}\s*(?:PAGE|STRANA)\s+(\d+)\s*-{3,}\s*(.*?)(?=(?:-{3,}\s*(?:PAGE|STRANA)\s+\d+\s*-{3,})|$)",
        full_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4
    margin = margin_cm * cm
    usable_width = width - 2 * margin
    usable_height = height - 2 * margin
    line_height = font_size * 1.5

    for page_number, page_text in matches:
        c.setFont(font_name, font_size)
        y = height - margin

        # Page header
        c.drawString(margin, y, f"Strana {page_number}")
        y -= line_height * 2

        paragraphs = page_text.strip().split("\n")
        for para in paragraphs:
            if not para.strip():
                y -= line_height
                continue

            wrapped_lines = simpleSplit(para.strip(), font_name, font_size, usable_width)
            for line in wrapped_lines:
                if y < margin + line_height:
                    c.showPage()
                    c.setFont(font_name, font_size)
                    y = height - margin
                    c.drawString(margin, y, f"Strana {page_number} (nastavak)")
                    y -= line_height * 2
                c.drawString(margin, y, line)
                y -= line_height

        c.showPage()

    c.save()
    print(f"✅ PDF saved to {output_pdf_path}")


if __name__ == '__main__':
    pass

    export_text_to_pdf(
        input_txt_path="../translated_pages/merged_serbian.txt",
        output_pdf_path="../translated_pages/serbian_book.pdf",
        font_size=11
    )