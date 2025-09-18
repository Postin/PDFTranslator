import os
import openai
import time
import re
from openai import RateLimitError
from config import OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def translate_text(page: str, target_language: str, system_prompt: None) -> str:
    """
    Uses OpenAI GPT to translate a text page into the specified language.

    Args:
        page (str): The input text to translate.
        target_language (str): The target language ("english", "serbian", "fr", etc.)
        system_prompt (str): Optional system instructions

    Returns:
        str: Translated text.
    """
    if system_prompt is None:
        system_prompt = (
            f"You are a professional translator. "
            f"Your task is to translate a page of text from a book "
            f"from English to {target_language}. "
            f"Return only the translated text in {target_language}, nothing else. "
            f"Write the translation in the following format:\n"
            f"#{target_language.title()}#\n...\n"
            f"Do not explain, summarize, or change the meaning of the original text. "
            f"Preserve the original structure and line breaks as much as possible. "
            f"Do not use styled or formatted text — keep the output in plain font."
        )

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini-2025-04-14",
                instructions=system_prompt,
                temperature=0.3,
                input=page
            )
            return response.output_text

        except RateLimitError as e:
            # Try to extract suggested wait time from error message
            msg = str(e)
            wait_time = 1000  # fallback
            match = re.search(r"retry after (\d+)s?", msg, re.IGNORECASE)
            if match:
                wait_time = int(match.group(1))
            elif hasattr(e, "retry_after") and e.retry_after:
                wait_time = int(e.retry_after)

            print(f"[WARN] Rate limit hit. Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"[ERROR] OpenAI translation failed: {e}")
            return ""

    print("[ERROR] Translation failed after maximum retries.")
    return ""