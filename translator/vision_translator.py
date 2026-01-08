import base64
import re
from io import BytesIO
from PIL import Image
from openai import OpenAI
from config import OPENAI_API_KEY
from utils.retry import retry_with_backoff

client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to base64-encoded PNG string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def parse_translation_response(response_text: str) -> dict:
    """
    Parse the GPT response into original and translated sections.
    
    Returns:
        dict: {"original": str, "translated": str}
    """
    original_match = re.search(
        r"#ORIGINAL#\s*(.*?)\s*(?=#TRANSLATED#|$)",
        response_text,
        re.DOTALL
    )
    translated_match = re.search(
        r"#TRANSLATED#\s*(.*?)$",
        response_text,
        re.DOTALL
    )
    
    return {
        "original": original_match.group(1).strip() if original_match else response_text,
        "translated": translated_match.group(1).strip() if translated_match else ""
    }


@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Translate extracted text from a text-based PDF page.
    
    Args:
        text: The extracted text to translate
        source_lang: Source language name
        target_lang: Target language name
        model: OpenAI model to use
        
    Returns:
        dict: {"original": str, "translated": str}
    """
    system_prompt = f"""You are a professional translator.

Your task:
1. Clean up and format the provided {source_lang} text (fix OCR errors, formatting issues)
2. Translate it into {target_lang}

Output format (use these EXACT markers):
#ORIGINAL#
[cleaned text in {source_lang}]

#TRANSLATED#
[translated text in {target_lang}]

Rules:
- Preserve the original structure, paragraphs, and meaning
- Do not summarize, explain, or add commentary
- Do not use markdown formatting
- Fix obvious OCR or extraction errors in the original"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        max_tokens=4096,
        temperature=0.2,
    )
    
    return parse_translation_response(response.choices[0].message.content)


@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def translate_image(
    image: Image.Image,
    source_lang: str,
    target_lang: str,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Extract text from a scanned page image using vision and translate it.
    
    Args:
        image: PIL Image of the scanned page
        source_lang: Source language name
        target_lang: Target language name
        model: OpenAI model to use
        
    Returns:
        dict: {"original": str, "translated": str}
    """
    base64_image = encode_image_to_base64(image)
    
    system_prompt = f"""You are a professional translator and OCR expert.

Your task:
1. Extract ALL text from this scanned page image in its original {source_lang} language
2. Translate the extracted text into {target_lang}

Output format (use these EXACT markers):
#ORIGINAL#
[extracted text in {source_lang}]

#TRANSLATED#
[translated text in {target_lang}]

Rules:
- Preserve the original structure, paragraphs, and line breaks
- Do not summarize, explain, or add commentary
- Do not use markdown formatting or styled text
- If text is unclear, make your best effort to transcribe it"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=4096,
        temperature=0.2,
    )
    
    return parse_translation_response(response.choices[0].message.content)
