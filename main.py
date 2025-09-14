import os
import logging
import asyncio
from io import BytesIO

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError(
        "Please set TELEGRAM_BOT_TOKEN and GOOGLE_API_KEY in your .env file"
    )

genai.configure(api_key=GOOGLE_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a text prompt and I'll generate an image using Gemini 2.5 Flash!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and generate images."""
    if not update.message or not update.message.text:
        return

    # Check if the message is in a group
    if update.message.chat.type not in ["group", "supergroup"]:
        return

    # Check if it's a forum group with topics
    if update.message.chat.is_forum:
        # In forum groups, only respond in topics
        if not (
            hasattr(update.message, "message_thread_id")
            and update.message.message_thread_id
        ):
            return
    # For regular groups, respond to all messages

    user_prompt = update.message.text
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username or "User"

    logger.info(f"Received prompt from {user_name} in {chat_id}: {user_prompt}")

    try:
        await update.message.reply_text(f"{user_name}, 🎨 generating image...")

        model = genai.GenerativeModel("gemini-2.5-flash-image-preview")

        response = await asyncio.to_thread(
            model.generate_content,
            f"Generate an image based on this prompt: {user_prompt}",
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
