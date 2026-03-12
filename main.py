import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.bot.access import AccessChecker
from src.bot.handlers import (
    BOT_DATA_ACCESS_CHECKER,
    BOT_DATA_IMAGE_SERVICE,
    error_handler,
    handle_message,
    start,
)
from src.config import Settings
from src.services.image import ImageService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GROUPS_CONFIG_PATH = Path(__file__).parent / "groups_config.json"


def main() -> None:
    settings = Settings.from_env()
    webhook_url = os.getenv("WEBHOOK_URL")

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data[BOT_DATA_IMAGE_SERVICE] = ImageService(settings)
    application.bot_data[BOT_DATA_ACCESS_CHECKER] = AccessChecker(GROUPS_CONFIG_PATH)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    if webhook_url:
        logger.info("Starting bot with webhook on port %s", settings.port)
        logger.info("Webhook URL: %s", webhook_url)
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.port,
            url_path="telegram",
            webhook_url=f"{webhook_url}/telegram",
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        logger.info(
            "No webhook URL and no PORT found — starting bot in polling mode (local dev)"
        )
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
