import os
import pyrogram
import logging
from chatbot.tasks import get_llm_answer

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

logger = logging.Logger("Telegram", 20)

def get_telegram_app():
    print(TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN)
    app = pyrogram.Client("bot", bot_token=TELEGRAM_BOT_TOKEN, api_hash=TELEGRAM_API_HASH, api_id=TELEGRAM_API_ID)
    print("app created")
    @app.on_message(pyrogram.filters.command("start"))
    def handle_notification(client, message):
        message.reply_text("سلام من دستیار هوشمند بانک گردشگری هستم. چطور می‌تونم کمکتون کنم؟")
    @app.on_message()
    def handle_query_message(client, message):
        print(message.text)
        message.reply_text(get_llm_answer(message))
    print("Starting App...")
    return app
