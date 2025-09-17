from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN  # Токен берем из config.py
import yt_dlp
import logging

# Создаем отдельный логгер только для бота
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

# Хендлер для записи в файл
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Отключаем лишние логи от httpx и telegram
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Отправь мне ссылку на Reels, и я пришлю видео.")


def get_video_from_instagram(url: str):
    try:
        ydl_opts = {
            "format": "mp4",
            "quiet": True,
            "outtmpl": "-",  # просто чтобы не качало в файл
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url")
    except Exception as e:
        logger.error(f"Ошибка при получении ссылки на видео: {e}")
        return None


async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text.strip()

    if "instagram.com/reel" not in text:
        await update.message.reply_text("Это не ссылка на Instagram Reels. Попробуй ещё раз.")
        return

    logger.info(f"Пользователь {user.id} (@{user.username}) {user.first_name} прислал ссылку: {text}")

    video_url = get_video_from_instagram(text)
    if not video_url:
        logger.warning(f"Не удалось получить видео по ссылке {text}")
        await update.message.reply_text("Не удалось найти видео. Возможно, ссылка битая или Reels приватный.")
        return

    try:
        # Скачиваем видео во временный файл
        ydl_opts = {
            "format": "mp4",
            "quiet": True,
            "outtmpl": "video.mp4",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        with open("video.mp4", "rb") as f:
            await update.message.reply_video(f)

        logger.info(f"Видео успешно отправлено пользователю {user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при отправке видео пользователю {user.id}: {e}")
        await update.message.reply_text("Произошла ошибка при получении видео.")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
