from exporter.pdf_exporter import export_text_to_pdf
from loader.image_loader import pdf_to_images
from translator.vision_translator import translate_image_with_vision_model
from merger.text_merger import merge_english_and_serbian
from tqdm import tqdm
import time
import os

# CONFIG VARIABLES
pdf_path = "data/Neurophilosophy.pdf"
output_path = "translated_output.txt"
MODEL = "gpt-4o"
SLEEP_SECONDS = 1.5
OUTPUT_DIR = "translated_pages"
MERGED_OUTPUT = "translated_book.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)


if __name__ == '__main__':

    # Get already translated page numbers (RESUME LOGIC)
    done_pages = {
        int(fname.split("_")[1].split(".")[0])
        for fname in os.listdir(OUTPUT_DIR)
        if fname.startswith("page_") and fname.endswith(".txt")
    }
    # CONVERT PDF TO IMAGES
    images = pdf_to_images(pdf_path)
    total_pages = len(images)

    print(f"📄 Starting translation of {total_pages} pages. Skipping {len(done_pages)} already done.\n")
    for i, img in enumerate(tqdm(images, desc="📚 Translating", unit="page")):
        page_num = i + 1
        out_path = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}.txt")

        if page_num in done_pages:
            continue  # Skip already translated pages

        try:
            translated = translate_image_with_vision_model(
                image=img,
                model=MODEL
            )
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(translated)
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            continue

        time.sleep(SLEEP_SECONDS)  # Rate limit buffer

    merge_english_and_serbian("translated_pages")
    export_text_to_pdf(
        input_txt_path="translated_pages/merged_serbian.txt",
        output_pdf_path="translated_pages/serbian_book.pdf",
        font_size=11
    )