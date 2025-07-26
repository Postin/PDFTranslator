import os
import re

def merge_english_and_serbian(
    input_dir: str = "translated_pages",
    english_output: str = "merged_english.txt",
    serbian_output: str = "merged_serbian.txt"
):
    """
    Merges all #English# and #Serbian# sections from per-page translation files
    into two separate output files, adding page numbers as headers.

    Args:
        input_dir (str): Folder with per-page translation files (e.g., page_001.txt).
        english_output (str): Output file path for merged English text.
        serbian_output (str): Output file path for merged Serbian text.
    """
    english_parts = []
    serbian_parts = []

    files = sorted([
        f for f in os.listdir(input_dir)
        if f.startswith("page_") and f.endswith(".txt")
    ])

    for filename in files:
        path = os.path.join(input_dir, filename)
        page_number = int(filename.split("_")[1].split(".")[0])

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

            english_match = re.search(r"#English#\s*(.*?)\s*(?=#Serbian#|$)", content, re.DOTALL)
            serbian_match = re.search(r"#Serbian#\s*(.*)", content, re.DOTALL)

            if english_match:
                english_text = english_match.group(1).strip()
                english_parts.append(f"--- PAGE {page_number} ---\n{english_text}")

            if serbian_match:
                serbian_text = serbian_match.group(1).strip()
                serbian_parts.append(f"--- STRANA {page_number} ---\n{serbian_text}")

    with open(os.path.join(input_dir, english_output), "w", encoding="utf-8") as f:
        f.write("\n\n".join(english_parts))

    with open(os.path.join(input_dir, serbian_output), "w", encoding="utf-8") as f:
        f.write("\n\n".join(serbian_parts))

    print(f"✅ Saved English to '{english_output}' and Serbian to '{serbian_output}' with page numbers.")


if __name__ == '__main__':
    merge_english_and_serbian("../translated_pages")