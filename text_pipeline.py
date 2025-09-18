from pathlib import Path
import os
import time
from loader.pdf_to_text import extract_text_from_pdf
from translator.text_translator import translate_text
from exporter.pdf_exporter import export_translation_to_pdf
from exporter.docx_exporter import export_translation_to_docx
from merger.text_merger import merge_source_and_target_texts
from checker.file_checker import check_files, delete_missing_files

def prepare_directories(pdf_path: Path) -> dict:
    bookname = pdf_path.stem
    base_data_dir = Path("data") / bookname
    translated_dir = base_data_dir / "translated_pages"

    # Ensure folders exist
    os.makedirs(translated_dir, exist_ok=True)

    return {
        "bookname": bookname,
        "translated_dir": translated_dir
    }


def translate_and_save(pages: list[str], target_lang: str, out_dir: str, done_pages: set):
    for i, page in enumerate(pages):
        page_num = i + 1
        out_path = os.path.join(out_dir, f"page_{page_num:03d}.txt")

        if args.resume and page_num in done_pages:
            continue

        print(f"Translating page {i+1}/{len(pages)}...")

        try:
            translation = translate_text(page, target_language=target_lang, system_prompt=None)
            if not translation:
                # Catch failed translate_text which returns empty string
                raise ValueError("translation is empty!")

            bilingual_output = (
                f"# English #\n"
                f"{page.strip()}\n\n"
                f"{translation.strip()}"
            )

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(bilingual_output)
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            continue

        time.sleep(args.sleep)


def save_translated_outputs(pages: list[str], output_dir: str, lang: str, to_pdf: bool, to_docx: bool):
    os.makedirs(output_dir, exist_ok=True)
    output_txt = Path(output_dir) / f"{lang}.txt"
    output_pdf = Path(output_dir) / f"{lang}.pdf"
    output_docx = Path(output_dir) / f"{lang}.docx"

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(pages))

    if to_pdf:
        export_translation_to_pdf(pages, str(output_pdf))
        pass

    if to_docx:
        export_translation_to_docx(str(output_txt), str(output_docx), language=lang)


def get_done_pages(translated_dir: Path):
    out_dir = translated_dir
    return {
        int(fname.split("_")[1].split(".")[0])
        for fname in os.listdir(out_dir)
        if fname.startswith("page_") and fname.endswith(".txt")
    }


def run_export_pipeline(translated_dir: Path, target_language: str, to_pdf = True, to_docx = True ):
    merged_eng = translated_dir / "merged_english.txt"

    merge_source_and_target_texts(
        input_dir=str(translated_dir),
        target_lang=target_language
    )

    if to_pdf:
        export_translation_to_pdf(str(merged_eng), str(translated_dir / f"{target_language}.pdf"), font_path=args.font,
                                  font_name=args.font_name)

    if to_docx:
        export_translation_to_docx(
            str(merged_eng), str(translated_dir / f"{target_language}.docx")
        )



def text_translation_pipeline(args):
    pdf_path = Path(args.pdf)
    lang = args.lang

    # Prepare directories
    print("[INFO] Preparing directories...")
    paths = prepare_directories(pdf_path)
    translated_dir = str(paths["translated_dir"])

    print("[INFO] Extracting text...")
    pages = extract_text_from_pdf(pdf_path)

    done_pages = get_done_pages(paths["translated_dir"])
    print("[INFO] Translating pages...")
    translate_and_save(pages, target_lang=lang, out_dir=translated_dir, done_pages=done_pages)

    print("[INFO] Checking file integrity...")
    missing_translation_files = check_files(translated_dir, lang)
    if missing_translation_files:
        print("[INFO] Deleting missing files...")
        delete_missing_files(translated_dir, missing_translation_files)
        print("[INFO] Translating missing pages...")
        translate_and_save(pages, target_lang=lang, out_dir=translated_dir, done_pages=done_pages)

    # print("[INFO] Saving outputs...")
    run_export_pipeline(paths["translated_dir"], args)


# Test pipeline
if __name__ == "__main__":
    from types import SimpleNamespace

    args = SimpleNamespace(
        pdf="data/GL-9_Print Ready.pdf",
        lang="german",
        font="fonts/DejaVuSans.ttf",
        font_name="DejaVuSans",
        to_pdf=True,
        to_docx=True,
        resume=True,
        output_dir="translated_pages",
        sleep=1.5,
    )
    text_translation_pipeline(args)
