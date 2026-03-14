import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.access import AccessChecker
from src.services.image import ImageService

logger = logging.getLogger(__name__)

BOT_DATA_IMAGE_SERVICE = "image_service"
BOT_DATA_ACCESS_CHECKER = "access_checker"
BOT_DATA_BOT_MODE = "bot_mode"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a text prompt and I'll generate an image using Gemini 2.5 Flash!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate an image for tagged messages in allowed groups/topics."""
    if not update.message or not update.message.text:
        return

    bot_username = context.bot.username
    is_private = update.message.chat.type == "private"
    bot_mode = context.bot_data.get(BOT_DATA_BOT_MODE, "group")

    # Проверка режима работы бота
    if is_private and bot_mode == "group":
        logger.warning("Ignoring message from private chat (bot mode is 'group')")
        return
    elif not is_private and bot_mode == "private":
        logger.warning("Ignoring message from group chat (bot mode is 'private')")
        return

    # В группах необходимо упоминание бота. В личке — опционально.
    has_mention = f"@{bot_username}" in update.message.text
    if not is_private and not has_mention:
        return

    chat_id = update.message.chat_id
    thread_id = update.message.message_thread_id
    chat_title = update.message.chat.title or "Private Chat"

    logger.info(
        "Message received from chat_title: '%s', chat_id: %s, thread_id: %s",
        chat_title,
        chat_id,
        thread_id,
    )

    access_checker: AccessChecker = context.bot_data[BOT_DATA_ACCESS_CHECKER]
    
    # Мы пропускаем проверку AccessChecker для личных сообщений
    if not is_private and not access_checker.is_allowed(chat_id, thread_id):
        logger.warning(
            "Access denied for chat_id=%s thread_id=%s", chat_id, thread_id
        )
        return

    # Убираем упоминание бота (если оно было), чтобы очистить промпт
    user_prompt = update.message.text.replace(f"@{bot_username}", "").strip()
    user_name = update.message.from_user.username or "User"
    user_id = update.message.from_user.id

    logger.info(
        "Generating image for %s (id: %s) in chat %s thread %s: %s",
        user_name,
        user_id,
        chat_id,
        thread_id,
        user_prompt,
    )

    try:
        await update.message.reply_text(f"{user_name}, generating image...")

        image_service: ImageService = context.bot_data[BOT_DATA_IMAGE_SERVICE]
        image_bytes = await image_service.generate(user_prompt, user_id=user_id)

        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"{user_name}, generated image for: {user_prompt}",
        )
    except ValueError as exc:
        logger.error("Image generation returned no result: %s", exc)
        await update.message.reply_text(
            f"{user_name}, no image was generated. Please try again."
        )
    except Exception as exc:
        logger.error("Unexpected error generating image: %s", exc)
        await update.message.reply_text(
            f"{user_name}, error generating image: {exc}"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log unexpected errors from the dispatcher."""
    logger.error("Exception while handling an update: %s", context.error)
