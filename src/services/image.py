import asyncio
import logging
from io import BytesIO

from google import genai
from google.genai import types

from src.config import Settings

logger = logging.getLogger(__name__)

GENERATION_TEMPERATURE = 0.7


class ImageService:
    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model_name = settings.gemini_model
        self._easter_egg = settings.easter_egg

    async def generate(self, prompt: str) -> BytesIO:
        """Generate an image for the given prompt and return it as BytesIO."""
        full_prompt = (
            f"Generate an image based on this prompt: {prompt}, "
            f"add a small easter-egg-style caption: {self._easter_egg}"
        )
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=GENERATION_TEMPERATURE,
            ),
        )

        if not response.candidates:
            raise ValueError("No candidates returned from Gemini API")

        candidate = response.candidates[0]
        if hasattr(candidate, "content") and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return BytesIO(part.inline_data.data)

        raise ValueError("No image data found in Gemini API response")
