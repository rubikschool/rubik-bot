import os
import json
import logging
import asyncio
from io import BytesIO
from urllib.request import Request, urlopen
from urllib.error import URLError

import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

IMAGE_GENERATION_TOPIC_NAME = "Image generation"
RUBIK_EASTER_EGG = "Rubik School"

METADATA_BASE_URL = "http://metadata.google.internal/computeMetadata/v1"
METADATA_HEADERS = {"Metadata-Flavor": "Google"}
METADATA_TIMEOUT_SECONDS = 3

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def _fetch_metadata(path: str) -> str:
    req = Request(f"{METADATA_BASE_URL}/{path}", headers=METADATA_HEADERS)
    with urlopen(req, timeout=METADATA_TIMEOUT_SECONDS) as resp:
        return resp.read().decode()


def _resolve_cloud_run_url() -> str | None:
    """Auto-detect the Cloud Run service URL via the metadata server and Admin API."""
    try:
        project_id = _fetch_metadata("project/project-id")
        region_path = _fetch_metadata("instance/region")
        region = region_path.split("/")[-1]
        service_name = os.getenv("K_SERVICE")
        if not service_name:
            return None

        token = json.loads(_fetch_metadata("instance/service-accounts/default/token"))["access_token"]

        api_url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}"
        req = Request(api_url, headers={"Authorization": f"Bearer {token}"})
        with urlopen(req, timeout=METADATA_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode()).get("uri")
    except (URLError, KeyError, json.JSONDecodeError) as exc:
        logger.warning("Could not auto-detect Cloud Run service URL: %s", exc)
        return None


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable is not set")
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a text prompt and I'll generate an image using Gemini 2.5 Flash!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and generate images."""
    if not update.message or not update.message.text:
        return

    # Check if the bot is mentioned in the message
    bot_username = context.bot.username
    if f"@{bot_username}" not in update.message.text:
        return

    chat_id = update.message.chat_id
    thread_id = update.message.message_thread_id

    logger.info(
        f"Received message from {update.message.from_user.username} in chat {chat_id}, thread {thread_id}: {update.message.text}"
    )

    # Check if the message is from a group (not private chat)
    if update.message.chat.type == "private":
        logger.warning("Message is from a private chat, generation not allowed")
        return

    user_prompt = update.message.text.replace(f"@{bot_username}", "").strip()
    user_name = update.message.from_user.username or "User"

    try:
        await update.message.reply_text(f"{user_name}, 🎨 generating image...")

        model = genai.GenerativeModel("gemini-2.5-flash-image-preview")

        response = await asyncio.to_thread(
            model.generate_content,
            f"Generate an image based on this prompt: {user_prompt}, add a small easter-egg-style caption: {RUBIK_EASTER_EGG}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
            ),
        )

        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]

            if hasattr(candidate, "content") and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data = part.inline_data.data
                        image_bytes = BytesIO(image_data)

                        await update.message.reply_photo(
                            photo=image_bytes,
                            caption=f"{user_name}, generated image for: {user_prompt}",
                        )
                        return

            await update.message.reply_text(
                f"{user_name}, ❌ no image was generated in the response."
            )
        else:
            await update.message.reply_text(
                f"{user_name}, ❌ failed to generate image. Please try again."
            )

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        await update.message.reply_text(
            f"{user_name}, ❌ error generating image: {str(e)}"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """Start the bot with webhook."""
    port = int(os.getenv("PORT", "8080"))

    webhook_url = _resolve_cloud_run_url()
    if not webhook_url:
        raise RuntimeError("Could not resolve Cloud Run service URL. Deploy to Cloud Run first.")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info(f"Starting bot with webhook on port {port}")
    logger.info(f"Webhook URL: {webhook_url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram",
        webhook_url=f"{webhook_url}/telegram",
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
