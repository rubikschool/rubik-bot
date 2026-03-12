import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash-image"
RUBIK_EASTER_EGG = "Rubik School"
DEFAULT_PORT = 8080


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    gemini_api_key: str
    port: int
    gemini_model: str = field(default=GEMINI_MODEL)
    easter_egg: str = field(default=RUBIK_EASTER_EGG)

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        port = int(os.getenv("PORT", str(DEFAULT_PORT)))

        return cls(
            telegram_bot_token=token,
            gemini_api_key=api_key,
            port=port,
        )
