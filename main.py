import os
import logging
import asyncio
from io import BytesIO
from typing import Optional

import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN and GOOGLE_API_KEY in your .env file")

genai.configure(api_key=GOOGLE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! Send me a text prompt and I\'ll generate an image using Gemini 2.5 Flash!'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and generate images."""
    if not update.message or not update.message.text:
        return

    user_prompt = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"Received prompt from {chat_id}: {user_prompt}")

    try:
        await update.message.reply_text("🎨 Generating image...")

        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

        response = await asyncio.to_thread(
            model.generate_content,
            f"Generate an image based on this prompt: {user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
            )
        )

        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]

            if hasattr(candidate, 'content') and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type

                        image_bytes = BytesIO(image_data)

                        await update.message.reply_photo(
                            photo=image_bytes,
                            caption=f"Generated image for: {user_prompt}"
                        )
                        return

            await update.message.reply_text("❌ No image was generated in the response.")
        else:
            await update.message.reply_text("❌ Failed to generate image. Please try again.")

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        await update.message.reply_text(f"❌ Error generating image: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()