import base64
import openai
from io import BytesIO
from PIL import Image
from openai import OpenAI

from config import OPENAI_API_KEY  # Import it from your config module
openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image_to_base64(image: Image.Image) -> str:
    """
    Converts a PIL image to base64-encoded PNG string.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def translate_image_with_vision_model(image: Image.Image, model: str = "gpt-4o",
                                      system_prompt: str = None) -> str:
    """
    Sends an image to a vision-capable OpenAI model and returns the translated text.

    Args:
        image (PIL.Image): Image of a scanned PDF page.
        model (str): Model to use (e.g., "gpt-4o", "gpt-4o-mini").
        system_prompt (str): Optional custom prompt for translation behavior.

    Returns:
        str: Translated page text.
    """
    base64_image = encode_image_to_base64(image)
    if system_prompt is None:
        system_prompt = (
            f"Ti si profesionalni prevodilac. "
            "Tvoj zadatak je da prevedeš sliku skenirane stranice iz knjige "
            "\"Neurophilosophy by Patricia Churchland\" sa engleskog na srpski (ekavica). "
            "Najpre prevedi sadržaj na jasan, prirodan i gramatički ispravan **engleski jezik**. "
            "Zatim, u posebnom pasusu, napiši prevod na **srpski jezik (ekavica)**. "
            "Koristi sledeće oznake za odeljke:\n"
            "#English#\n... \n#Serbian#\n... \n"
            "Ne objašnjavaj, ne rezimiraj i ne menjaј smisao originalnog teksta. "
            "Gde god je moguće, sačuvaj strukturu teksta i raspored redova. "
            "Nemoj koristiti stilizovani tekst ili formatiranje, tekst treba da bude u običnom fontu."
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2048,
        temperature=0.3,
    )

    return response.choices[0].message.content
