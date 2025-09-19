import os
import pyrogram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


app = pyrogram.Client("bot", bot_token=TELEGRAM_BOT_TOKEN, api_hash=TELEGRAM_API_HASH, api_id=TELEGRAM_API_ID)

@app.on_message(pyrogram.filters.command("start"))
def handle_notification(client, message):
    message.reply_text("سلام من دستیار هوشمند بانک گردشگری هستم. چطور می‌تونم کمکتون کنم؟")
