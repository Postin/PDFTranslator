from pdf2image import convert_from_path
from PIL import Image
import os
from typing import List

def pdf_to_images(
    pdf_path: str,
    cache_dir: str = "data/images",
    dpi: int = 200,
) -> List[Image.Image]:
    """
    Converts PDF pages to images and caches them as PNGs.
    If images already exist, loads from disk instead of recomputing.

    Args:
        pdf_path (str): Path to PDF file.
        cache_dir (str): Directory to save/load cached PNGs.
        dpi (int): Resolution for rendering.

    Returns:
        List[Image.Image]: List of PIL images for each page.
    """
    os.makedirs(cache_dir, exist_ok=True)

    # Filter for cached page images
    cached_files = sorted(
        [f for f in os.listdir(cache_dir) if f.startswith("page_") and f.endswith(".png")]
    )

    if cached_files:
        print(f"📦 Using cached images in '{cache_dir}'...")
        return [Image.open(os.path.join(cache_dir, fname)) for fname in cached_files]

    print("🖼 No cached images found. Converting PDF to images...")
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=r"C:\poppler-24.08.0\Library\bin")

    for i, img in enumerate(images):
        img.save(os.path.join(cache_dir, f"page_{i+1:03d}.png"), "PNG")

    print(f"✅ Saved {len(images)} images to '{cache_dir}'")
    return images


# def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
#     """
#     Converts PDF pages to a list of PIL Images.
#
#     Args:
#         pdf_path (str): Path to PDF file.
#         dpi (int): Resolution for rendering.
#
#     Returns:
#         List[Image.Image]: List of images (one per page).
#     """
#     images = convert_from_path(pdf_path, dpi=dpi, poppler_path=r"C:\poppler-24.08.0\Library\bin")
#     return images
