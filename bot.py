# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import instaloader
import requests
from config import TOKEN  # Импортируем токен

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Отправь мне ссылку на Reels, и я отправлю видео в Telegram.")

def get_video_from_instagram(url: str):
    L = instaloader.Instaloader()
    try:
        post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
        video_url = post.video_url
        return video_url
    except Exception as e:
        return None  # Если не удалось получить видео

async def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if "instagram.com/reel" not in url:
        await update.message.reply_text("Это не ссылка на Instagram Reels. Пожалуйста, отправь правильную ссылку.")
        return

    video_url = get_video_from_instagram(url)
    if video_url:
        try:
            video_response = requests.get(video_url)
            if video_response.status_code == 200:
                await update.message.reply_video(video_response.content)
            else:
                await update.message.reply_text("Не удалось скачать видео. Возможно, оно недоступно.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при получении видео: {e}")
    else:
        await update.message.reply_text("Не удалось найти видео по этой ссылке. Возможно, оно недоступно или ограничено.")

def main():
    application = Application.builder().token(TOKEN).build()  # Используем токен из config.py

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
