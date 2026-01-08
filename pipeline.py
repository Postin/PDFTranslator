import os
import json
import threading
from typing import Callable, Optional
from tqdm import tqdm

from loader.image_loader import load_pdf
from translator.vision_translator import translate_text, translate_image
from exporter.docx_exporter import create_bilingual_docx
from exporter.pdf_exporter import create_bilingual_pdf
from utils.parallel import parallel_translate, sequential_translate

# Thread lock for safe cache file writes
_cache_lock = threading.Lock()


def create_translate_function(source_lang: str, target_lang: str, model: str) -> Callable:
    """
    Create a translation function configured with language settings.
    
    Returns:
        Callable that takes a page dict and returns translation result
    """
    def translate_page(page: dict) -> dict:
        if page["type"] == "text":
            return translate_text(
                text=page["content"],
                source_lang=source_lang,
                target_lang=target_lang,
                model=model
            )
        else:
            return translate_image(
                image=page["content"],
                source_lang=source_lang,
                target_lang=target_lang,
                model=model
            )
    
    return translate_page


def run_translation_pipeline(
    args,
    progress_callback: Optional[Callable[[int, int, dict], None]] = None
) -> dict:
    """
    Main translation pipeline.
    
    Processes a PDF file, translates each page in parallel, and outputs 
    bilingual documents (DOCX and/or PDF).
    
    Args:
        args: CLI arguments or config object with attributes:
            - pdf: Path to PDF file
            - source_lang: Source language
            - target_lang: Target language
            - model: OpenAI model
            - output: Output file path (optional)
            - format: Output format (docx, pdf, both)
            - resume: Whether to resume from cache
            - output_dir: Cache directory
            - dpi: Image resolution
            - workers: Number of parallel workers
            - sleep: Sleep between API calls
        progress_callback: Optional callback(completed, total, result) for progress updates
        
    Returns:
        dict: Translation results by page number
    """
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine output filenames
    pdf_name = os.path.splitext(os.path.basename(args.pdf))[0]
    
    if args.output:
        base_output = os.path.splitext(args.output)[0]
    else:
        base_output = f"{pdf_name}_translated"
    
    output_docx = f"{base_output}.docx"
    output_pdf = f"{base_output}.pdf"
    
    # Cache file for resume support
    cache_file = os.path.join(output_dir, "translation_cache.json")
    translated_pages = {}
    
    # Load cached translations if resuming
    if args.resume and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            translated_pages = json.load(f)
        print(f"Resuming: found {len(translated_pages)} cached pages")
    
    # Load PDF and analyze pages
    print(f"\nLoading PDF: {args.pdf}")
    pages = load_pdf(
        args.pdf,
        cache_dir=os.path.join(output_dir, "images"),
        dpi=args.dpi
    )
    total_pages = len(pages)
    
    # Filter out already translated pages
    pages_to_translate = [p for p in pages if str(p["page_num"]) not in translated_pages]
    
    if not pages_to_translate:
        print("All pages already translated!")
    else:
        print(f"\nTranslating {len(pages_to_translate)} pages ({args.source_lang} -> {args.target_lang})")
        print(f"Model: {args.model}, Workers: {args.workers}\n")
        
        # Create translation function
        translate_func = create_translate_function(
            args.source_lang, 
            args.target_lang, 
            args.model
        )
        
        # Progress bar for CLI
        pbar = tqdm(total=len(pages_to_translate), desc="Translating", unit="page")
        
        def cli_progress(completed, total, result):
            pbar.update(1)
            # Save to cache after each page (thread-safe)
            if "error" not in result:
                with _cache_lock:
                    translated_pages[str(result["page_num"])] = result
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(translated_pages, f, ensure_ascii=False, indent=2)
            # Call external progress callback if provided
            if progress_callback:
                progress_callback(
                    len(translated_pages), 
                    total_pages, 
                    result
                )
        
        # Run translation (parallel or sequential based on workers)
        try:
            if args.workers > 1:
                new_results = parallel_translate(
                    pages=pages_to_translate,
                    translate_func=translate_func,
                    max_workers=args.workers,
                    progress_callback=cli_progress
                )
            else:
                new_results = sequential_translate(
                    pages=pages_to_translate,
                    translate_func=translate_func,
                    progress_callback=cli_progress,
                    sleep_between=args.sleep
                )
            
            # Merge results
            translated_pages.update(new_results)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted! Saving progress...")
        finally:
            pbar.close()
            # Always save final state
            with _cache_lock:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(translated_pages, f, ensure_ascii=False, indent=2)
            print(f"Progress saved: {len(translated_pages)} pages cached")
    
    # Prepare pages list in order
    pages_list = []
    for i in range(1, total_pages + 1):
        page_key = str(i)
        if page_key in translated_pages:
            pages_list.append(translated_pages[page_key])
    
    # Create output documents
    output_format = getattr(args, 'format', 'docx')
    
    print(f"\nCreating output documents...")
    
    if output_format in ("docx", "both"):
        create_bilingual_docx(
            pages=pages_list,
            output_path=output_docx,
            source_lang=args.source_lang,
            target_lang=args.target_lang
        )
    
    if output_format in ("pdf", "both"):
        create_bilingual_pdf(
            pages=pages_list,
            output_path=output_pdf,
            source_lang=args.source_lang,
            target_lang=args.target_lang
        )
    
    print(f"\nTranslation complete!")
    print(f"Pages translated: {len(pages_list)}/{total_pages}")
    
    return translated_pages
