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


def merge_source_and_target_texts(
    input_dir: str = "translated_pages",
    source_lang: str = "English",
    target_lang: str = "Serbian",
    source_output: str = "merged_source.txt",
    target_output: str = "merged_target.txt",
    source_page_label: str = "PAGE",
    target_page_label: str = "STRANA"
):
    """
    Merges #<SourceLang># and #<TargetLang># sections from per-page files into two outputs.

    Args:
        input_dir (str): Folder with per-page .txt translation files.
        source_lang (str): Name of the source language (e.g. "English").
        target_lang (str): Name of the target language (e.g. "Serbian").
        source_output (str): Output .txt file name for merged source text.
        target_output (str): Output .txt file name for merged target text.
        source_page_label (str): Page header label for source (e.g., "PAGE").
        target_page_label (str): Page header label for target (e.g., "STRANA").
    """

    source_parts = []
    target_parts = []

    files = sorted([
        f for f in os.listdir(input_dir)
        if f.startswith("page_") and f.endswith(".txt")
    ])

    for filename in files:
        path = os.path.join(input_dir, filename)
        page_number = int(filename.split("_")[1].split(".")[0])

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

            source_match = re.search(
                fr"#\s*{re.escape(source_lang)}\s*#\s*(.*?)\s*(?=#\s*{re.escape(target_lang)}\s*#|$)",
                content, re.DOTALL | re.IGNORECASE
            )

            target_match = re.search(fr"#{re.escape(target_lang)}#\s*(.*)", content, re.DOTALL | re.IGNORECASE )

            if source_match:
                source_text = source_match.group(1).strip()
                source_parts.append(f"--- {source_page_label} {page_number} ---\n{source_text}")

            if target_match:
                target_text = target_match.group(1).strip()
                target_parts.append(f"--- {target_page_label} {page_number} ---\n{target_text}")

    with open(os.path.join(input_dir, source_output), "w", encoding="utf-8") as f:
        f.write("\n\n".join(source_parts))

    with open(os.path.join(input_dir, target_output), "w", encoding="utf-8") as f:
        f.write("\n\n".join(target_parts))

    print(f"✅ Saved {source_lang} to '{source_output}' and {target_lang} to '{target_output}' with page headers.")
    return source_output, target_output


if __name__ == '__main__':
    # merge_english_and_serbian("../translated_pages")
    merge_source_and_target_texts(input_dir="../data/GL-9_Print Ready/translated_pages")