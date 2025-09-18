from pdf2image import convert_from_path
from PIL import Image
import os
from typing import List, Optional


def pdf_to_images(
    pdf_path: str,
    cache_dir: str = "data/images",
    dpi: int = 200,
    poppler_path: Optional[str] = None,
) -> List[Image.Image]:
    """
    Converts PDF pages to images and caches them as PNGs.
    If images already exist, loads from disk instead of recomputing.

    Args:
        pdf_path (str): Path to PDF file.
        cache_dir (str): Directory to save/load cached PNGs.
        dpi (int): Resolution for rendering.
        poppler_path (str): Optional path to poppler bin directory (Windows only).

    Returns:
        List[Image.Image]: List of PIL images for each page.
    """
    os.makedirs(cache_dir, exist_ok=True)

    cached_files = sorted(
        [f for f in os.listdir(cache_dir) if f.startswith("page_") and f.endswith(".png")]
    )

    if cached_files:
        print(f"📦 Using cached images in '{cache_dir}'...")
        return [Image.open(os.path.join(cache_dir, fname)) for fname in cached_files]

    print("🖼 No cached images found. Converting PDF to images...")

    # Use dynamic poppler path or fall back to env
    poppler_path = poppler_path or os.getenv("POPPLER_PATH")

    try:
        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    except Exception as e:
        raise RuntimeError(
            f"PDF to image conversion failed. Ensure Poppler is installed and 'poppler_path' is set.\n{e}"
        )

    for i, img in enumerate(images):
        img.save(os.path.join(cache_dir, f"page_{i+1:03d}.png"), "PNG")

    print(f"✅ Saved {len(images)} images to '{cache_dir}'")
    return images