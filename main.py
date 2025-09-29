import os
import logging
import asyncio
import json
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

allowed_threads = {}


def load_config():
    """Load and parse the groups_config.json file."""
    global allowed_threads
    try:
        with open("groups_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            allowed_groups = config.get("allowed_groups", [])
            for group in allowed_groups:
                group_id = group.get("group_id")
                if group_id:
                    allowed_threads[group_id] = set()
                    for topic in group.get("topics", []):
                        if topic.get("topic_name") == IMAGE_GENERATION_TOPIC_NAME:
                            thread_id = topic.get("thread_id")
                            if thread_id:
                                allowed_threads[group_id].add(thread_id)
            logger.info(f"Loaded config for allowed threads: {allowed_threads}")
    except FileNotFoundError:
        logger.error("groups_config.json not found.")
    except json.JSONDecodeError:
        logger.error("Error decoding groups_config.json.")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError(
        "Please set TELEGRAM_BOT_TOKEN and GOOGLE_API_KEY in your .env file"
    )

genai.configure(api_key=GOOGLE_API_KEY)


class HealthcheckHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for Cloud Run health checks."""

    def do_GET(self):  # noqa: N802 (keep method name for BaseHTTPRequestHandler)
        if self.path in ("/ready", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):  # silence default verbose logging
        return


def start_healthcheck_server() -> None:
    server = HTTPServer(("0.0.0.0", 8080), HealthcheckHandler)
    logger.info("Healthcheck server listening on 0.0.0.0: 8080")
    server.serve_forever()


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

    # Check if the message is from an allowed group and topic
    if not (
        thread_id
        and chat_id in allowed_threads
        and thread_id in allowed_threads.get(chat_id, set())
    ):
        logger.warning("Message is not from an allowed group and topic")
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
    """Start the bot."""
    # Start lightweight HTTP server for Cloud Run health checks
    Thread(target=start_healthcheck_server, daemon=True).start()

    load_config()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
