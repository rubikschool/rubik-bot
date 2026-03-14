import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash-image"
DEFAULT_LOGO_PATH = "logo.png"
DEFAULT_LOGO_POSITION = "bottom-right corner"
DEFAULT_PORT = 8080
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    gemini_api_key: str
    port: int
    webhook_url: str | None = None
    gemini_model: str = field(default=GEMINI_MODEL)
    logo_path: Path = field(default_factory=lambda: Path(DEFAULT_LOGO_PATH))
    logo_position: str = field(default=DEFAULT_LOGO_POSITION)
    bot_mode: str = field(default="group")

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        port = int(os.getenv("PORT", str(DEFAULT_PORT)))
        webhook_url = os.getenv("WEBHOOK_URL")
        logo_path = Path(os.getenv("LOGO_PATH", DEFAULT_LOGO_PATH))
        if not logo_path.is_absolute():
            logo_path = PROJECT_ROOT / logo_path
        logo_position = os.getenv("LOGO_POSITION", DEFAULT_LOGO_POSITION)
        
        # Режим работы бота: "group" (только группы), "private" (только личка), "both" (и там, и там)
        bot_mode = os.getenv("BOT_MODE", "group").lower()

        return cls(
            telegram_bot_token=token,
            gemini_api_key=api_key,
            port=port,
            webhook_url=webhook_url,
            logo_path=logo_path,
            logo_position=logo_position,
            bot_mode=bot_mode,
        )
