import os
import time
from loader.image_loader import pdf_to_images
from translator.vision_translator import translate_image_with_vision_model
from merger.text_merger import merge_english_and_serbian
from exporter.pdf_exporter import export_text_to_pdf
from exporter.docx_exporter import export_translation_to_docx
from pathlib import Path


def run_translation_pipeline(args):
    pdf_path = Path(args.pdf)
    bookname = pdf_path.stem  # Extracts "book" from "book.pdf"
    base_data_dir = Path("data") / bookname
    image_dir = base_data_dir / "images"
    translated_dir = base_data_dir / "translated_pages"

    # Ensure folders exist
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(translated_dir, exist_ok=True)

    out_dir = str(translated_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Step 1: Load or convert PDF to images
    images = pdf_to_images(pdf_path=str(pdf_path), cache_dir=str(image_dir), dpi=args.dpi)

    # Step 2: Detect already translated pages
    done_pages = {
        int(fname.split("_")[1].split(".")[0])
        for fname in os.listdir(out_dir)
        if fname.startswith("page_") and fname.endswith(".txt")
    }

    # Step 3: Translate pages
    for i, img in enumerate(images):
        page_num = i + 1
        out_path = os.path.join(out_dir, f"page_{page_num:03d}.txt")

        if args.resume and page_num in done_pages:
            continue

        print(f"📄 Translating page {page_num}/{len(images)}...")

        try:
            translation = translate_image_with_vision_model(
                image=img,
                model=args.model
            )

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(translation)

        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            continue

        time.sleep(args.sleep)

    # Step 4: Merge and export
    merged_eng = os.path.join(out_dir, "merged_english.txt")
    merged_srp = os.path.join(out_dir, "merged_serbian.txt")

    if args.lang in ["english", "srpski", "both"]:
        merge_english_and_serbian(input_dir=out_dir,
                                  english_output=os.path.basename(merged_eng),
                                  serbian_output=os.path.basename(merged_srp))

    if args.to_pdf:
        if str.lower(args.lang) in ["english", "both"]:
            export_text_to_pdf(merged_eng, str(translated_dir / 'english.pdf'), font_path=args.font,
                               font_name=args.font_name)
        if str.lower(args.lang) in ["srpski", "both"]:
            export_text_to_pdf(merged_srp, str(translated_dir / 'srpski.pdf'), font_path=args.font,
                               font_name=args.font_name)

    if args.to_docx:
        if str.lower(args.lang) in ["english", "both"]:
            export_translation_to_docx(merged_eng,  str(translated_dir / 'english.docx'), language="English")
        if str.lower(args.lang) in ["srpski", "both"]:
            export_translation_to_docx(merged_srp, str(translated_dir / 'srpski.docx'), language="Srpski")


# Test pipeline
if __name__ == "__main__":
    from types import SimpleNamespace

    args = SimpleNamespace(
        pdf="data/Neurophilosophy.pdf",
        lang="srpski",  # or "srpski", "english"
        model="gpt-4o",
        font="fonts/DejaVuSans.ttf",
        font_name="DejaVuSans",
        to_pdf=True,
        to_docx=True,
        resume=True,
        output_dir="translated_pages",
        dpi=200,
        sleep=1.5,
    )
    run_translation_pipeline(args)
