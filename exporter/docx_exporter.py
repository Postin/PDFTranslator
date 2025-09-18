from docx import Document
from docx.shared import Pt
import re
import os


def export_translation_to_docx(
    input_txt_path: str,
    output_docx_path: str,
    language: str = "Srpski"
):
    """
    Converts a merged translation file to a DOCX file,
    with each logical page in its own section.

    Args:
        input_txt_path (str): Path to merged_english.txt or merged_serbian.txt
        output_docx_path (str): Destination .docx file path
        language (str): Optional label (used in headers)
    """

    if not os.path.exists(input_txt_path):
        print(f"❌ File not found: {input_txt_path}")
        return

    with open(input_txt_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Match page headers and content
    matches = re.findall(
        r"-{3,}\s*(?:PAGE|STRANA)\s+(\d+)\s*-{3,}\s*(.*?)(?=(?:-{3,}\s*(?:PAGE|STRANA)\s+\d+\s*-{3,})|$)",
        full_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    doc = Document()

    # Set base font style
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(12)

    for page_number, page_text in matches:
        # Add a heading for the page
        doc.add_heading(f"Page {page_number}", level=2)

        # Split paragraphs
        for para in page_text.strip().split("\n"):
            if para.strip():
                doc.add_paragraph(para.strip())

        # Page break after each section
        # doc.add_page_break()

    doc.save(output_docx_path)
    print(f"✅ Word document saved to: {output_docx_path}")


if __name__ == '__main__':
    # pass
    export_translation_to_docx(
        input_txt_path="../data/GL-9_Print Ready/translated_pages/merged_source.txt",
        output_docx_path="../data/GL-9_Print Ready/translated_pages/book.docx",
        language="German"
    )