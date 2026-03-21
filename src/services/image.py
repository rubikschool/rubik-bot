import asyncio
import json
import logging
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types

from src.config import Settings

logger = logging.getLogger(__name__)

GENERATION_TEMPERATURE = 1


class ImageService:
    def __init__(self, settings: Settings, groups_config_path: Path) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model_name = settings.gemini_model
        self._easter_egg = getattr(settings, "easter_egg", "Kubik rubik")
        self._users_easter_eggs = self._load_users_config(groups_config_path)

    def _load_users_config(self, config_path: Path) -> dict[int, str]:
        try:
            with config_path.open(encoding="utf-8") as f:
                data = json.load(f)
            users_list = data.get("users", [])
            return {user["tg_id"]: user["easter_egg_text"] for user in users_list if "tg_id" in user and "easter_egg_text" in user}
        except Exception as e:
            logger.error("Failed to load users config for easter eggs: %s", e)
            return {}

    async def generate(self, prompt: str, user_id: int | None = None) -> BytesIO:
        """Generate an image for the given prompt and return it as BytesIO."""
        easter_egg = self._users_easter_eggs.get(user_id, self._easter_egg) if user_id else self._easter_egg
        full_prompt = (
            f"Generate an image based on this prompt: {prompt}, "
            f"add a small easter-egg-style caption: {easter_egg}"
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
