import os
import time
from loader.pdf_to_images import pdf_to_images
from translator.vision_translator import translate_image_with_vision_model
from merger.text_merger import merge_english_and_serbian
from exporter.pdf_exporter import export_translation_to_pdf
from exporter.docx_exporter import export_translation_to_docx
from pathlib import Path


def prepare_directories(pdf_path: Path) -> dict:
    bookname = pdf_path.stem
    base_data_dir = Path("data") / bookname
    image_dir = base_data_dir / "images"
    translated_dir = base_data_dir / "translated_pages"

    # Ensure folders exist
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(translated_dir, exist_ok=True)

    return {
        "bookname": bookname,
        "image_dir": image_dir,
        "translated_dir": translated_dir
    }


def load_images(pdf_path: str, image_dir: str, dpi: int):
    return pdf_to_images(pdf_path=pdf_path, cache_dir=image_dir, dpi=dpi)


def get_done_pages(translated_dir: Path):
    out_dir = translated_dir
    return {
        int(fname.split("_")[1].split(".")[0])
        for fname in os.listdir(out_dir)
        if fname.startswith("page_") and fname.endswith(".txt")
    }


def translate_and_save(images, out_dir: str, args, done_pages: set):
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


def run_export_pipeline(translated_dir: Path, args):
    merged_eng = translated_dir / "merged_english.txt"
    merged_srp = translated_dir / "merged_serbian.txt"

    if args.lang in ["english", "srpski", "both"]:
        merge_english_and_serbian(
            input_dir=str(translated_dir),
            english_output=merged_eng.name,
            serbian_output=merged_srp.name
        )

    if args.to_pdf:
        if args.lang.lower() in ["english", "both"]:
            export_translation_to_pdf(str(merged_eng), str(translated_dir / "english.pdf"), font_path=args.font,
                                      font_name=args.font_name)
        if args.lang.lower() in ["srpski", "both"]:
            export_translation_to_pdf(str(merged_srp), str(translated_dir / "srpski.pdf"), font_path=args.font,
                                      font_name=args.font_name)

    if args.to_docx:
        if args.lang.lower() in ["english", "both"]:
            export_translation_to_docx(
                str(merged_eng), str(translated_dir / "english.docx"), language="English"
            )
        if args.lang.lower() in ["srpski", "both"]:
            export_translation_to_docx(
                str(merged_srp), str(translated_dir / "srpski.docx"), language="Srpski"
            )


def run_vision_translation_pipeline(args):
    pdf_path = Path(args.pdf)
    paths = prepare_directories(pdf_path)

    images = load_images(
        pdf_path=str(pdf_path),
        image_dir=str(paths["image_dir"]),
        dpi=args.dpi
    )

    done_pages = get_done_pages(paths["translated_dir"])
    translate_and_save(images, str(paths["translated_dir"]), args, done_pages)
    run_export_pipeline(paths["translated_dir"], args)


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
    run_vision_translation_pipeline(args)
