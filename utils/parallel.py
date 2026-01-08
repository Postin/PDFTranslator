import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Optional

logger = logging.getLogger(__name__)


def parallel_translate(
    pages: List[dict],
    translate_func: Callable,
    max_workers: int = 3,
    progress_callback: Optional[Callable[[int, int, dict], None]] = None
) -> dict:
    """
    Process pages in parallel with a translation function.
    
    Args:
        pages: List of page dicts with {"page_num": int, "content": str|Image, "type": str}
        translate_func: Function that takes a page dict and returns {"original": str, "translated": str}
        max_workers: Maximum number of parallel workers
        progress_callback: Optional callback(completed, total, result) for progress updates
        
    Returns:
        dict: Mapping of page_num (str) to translation result
    """
    results = {}
    total = len(pages)
    completed = 0
    
    def process_page(page: dict) -> tuple:
        """Process a single page and return (page_num, result)."""
        page_num = page["page_num"]
        try:
            result = translate_func(page)
            result["page_num"] = page_num
            return page_num, result, None
        except Exception as e:
            logger.error(f"Error translating page {page_num}: {e}")
            return page_num, None, str(e)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_page = {
            executor.submit(process_page, page): page 
            for page in pages
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_page):
            page_num, result, error = future.result()
            completed += 1
            
            if result:
                results[str(page_num)] = result
                
                if progress_callback:
                    progress_callback(completed, total, result)
            else:
                logger.warning(f"Page {page_num} failed: {error}")
                if progress_callback:
                    progress_callback(completed, total, {"page_num": page_num, "error": error})
    
    return results


def sequential_translate(
    pages: List[dict],
    translate_func: Callable,
    progress_callback: Optional[Callable[[int, int, dict], None]] = None,
    sleep_between: float = 0
) -> dict:
    """
    Process pages sequentially (fallback for when parallel isn't desired).
    
    Args:
        pages: List of page dicts
        translate_func: Translation function
        progress_callback: Progress callback
        sleep_between: Sleep time between pages
        
    Returns:
        dict: Mapping of page_num (str) to translation result
    """
    import time
    
    results = {}
    total = len(pages)
    
    for i, page in enumerate(pages):
        page_num = page["page_num"]
        
        try:
            result = translate_func(page)
            result["page_num"] = page_num
            results[str(page_num)] = result
            
            if progress_callback:
                progress_callback(i + 1, total, result)
                
        except Exception as e:
            logger.error(f"Error translating page {page_num}: {e}")
            if progress_callback:
                progress_callback(i + 1, total, {"page_num": page_num, "error": str(e)})
        
        if sleep_between > 0 and i < len(pages) - 1:
            time.sleep(sleep_between)
    
    return results

