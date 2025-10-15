import os
import random
import time
from datetime import timedelta
from django.utils import timezone

import pyrogram
from pyrogram.enums import ChatAction
import logging

from pyrogram.raw.base import reply_markup
from chatbot.tasks import get_llm_answer, get_history_messages, send_request_to_endpoint, analyze_state_of_messaging
from telegram.models import TelegramMessage, UserMessage, BotMessage, Alert, TelegramSummary, SendTelegramMessageRequest
from chatbot.models import Document, FAQ
from celery import shared_task

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
AGENT_IDS = [311701038]
SELF_USER_ID = 7165380042
USER_MESSAGE_SYSTEM_PROMPT = """You are a smart hotel booking assistant available to hotel users via a telegram bot. Your sole source of knowledge is the official Hotel Knowledge Tree provided below.  
The Knowledge Tree is structured as a list of Documents and FAQS.
Each Document has a category, sub_category, and solution.
Each FAQ has a category, question, and answer.
You must ONLY generate answers strictly based on the Knowledge Tree.  
Do not invent, guess, or provide any information outside of the Knowledge Tree.
Answer in Persian.

{DATA}

🎯 Your objectives:
- Provide accurate, concise, and clear answers to hotel booking-related questions.
- Always ensure the answer has the strongest possible relevance to the user's question.
- Respect the boundaries of the Knowledge Tree: no outside knowledge, no assumptions.
- In case of repeated questions, try to find what the user is asking for and provide the most relevant answer and try to guide the user to better ask their question.

📌 Behavioral Rules:
1. Answer ONLY from the Knowledge Tree. If no relevant entry exists, say:  
   "This question is not covered in the official hotel booking resources, and I cannot provide an answer."  
2. If the user’s question is outside the hotel booking domain (e.g., sports, movies, personal advice), politely decline and say:  
   "This question is outside the scope of hotel booking services, and I cannot provide an answer."  
3. If the user’s question is ambiguous or incomplete, do NOT guess.  
   - Instead, ask a clarifying question to make sure you fully understand before answering.  
   Example:  
   User: "I want to book a hotel."  
   Assistant: "Could you please specify which type of hotel you are interested in (luxury, budget, or mid-range) so I can provide accurate requirements?"  
4. Responses should be:  
   - Short and precise (max 3–5 sentences).  
   - Written in a polite, professional, and user-friendly tone.  
   - Always directly relevant to the user’s intent.  
5. Never provide hotel booking recommendations, personal opinions, or unverified advice.  

⚠️ Remember: You must ALWAYS act strictly within these rules and base your answers ONLY on the Knowledge Tree.

After answering the question, ask the user if they have any other questions and suggest some other questions related to their problem.
"""

ANALYZE_INCOMING_MESSAGES_SYSTEM_PROMPT = """You are a smart question and answers analyzer. You are given a list of questions sent to us from hotel booking users. Analyze the questions and answers and find 5 most common questions. 
Skip any questions irrelevant to hotel booking services. Write the top questions seperately to be send to a human agent. Write in persian."""

logger = logging.Logger("Telegram", 20)

def get_telegram_app():
    app = pyrogram.Client("bot", bot_token=TELEGRAM_BOT_TOKEN, api_hash=TELEGRAM_API_HASH, api_id=TELEGRAM_API_ID)
    @app.on_callback_query(pyrogram.filters.regex(r"^rate&"))
    def handle_callback_query(client, callback_query):
        _, id_str, rate_str = callback_query.data.split("&")
        id, rate = int(id_str), int(rate_str)
        set_message_rate.delay(id, rate)
        callback_query.edit_message_text(BotMessage.objects.get(id=id).text, reply_markup=None)
        callback_query.answer("با تشکر از امتیاز شما")
    
    @app.on_message(pyrogram.filters.command("start"))
    def handle_notification(client, message):
        message.reply_text("سلام من دستیار هوشمند ایوان هستم. چطور می‌تونم کمکتون کنم؟")
    @app.on_message()
    def handle_query_message(client, message):
        if message.from_user.id == SELF_USER_ID:
            return
        client.send_chat_action(message.chat.id, ChatAction.TYPING)
        bot_answer = get_llm_answer(message.text, USER_MESSAGE_SYSTEM_PROMPT.format(DATA=get_docs_and_faq_data(request=message.text)), get_history_messages(message.from_user.id, message.chat.id))
        
        state = analyze_state_of_messaging(message.text, bot_answer)
        question_answer_state = state if state in ["ANSWERED", "UNKNOWN", "IRRELEVANT"] else "ANSWERED"
        keyboard = None
        user_message = UserMessage.objects.create(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            text=message.text,
            state=question_answer_state
        )
        bot_message = BotMessage.objects.create(user_message=user_message, text=bot_answer)
        if question_answer_state == "ANSWERED" and random.random() < 0.4:
            keyboard = pyrogram.types.InlineKeyboardMarkup([
                [pyrogram.types.InlineKeyboardButton("لطفا به جواب ربات امتیاز دهید.", callback_data="random")],
                [
                    pyrogram.types.InlineKeyboardButton(f"{i}", callback_data=f"rate&{bot_message.id}&{i}") for i in range(1, 6)
                ]
            ])
        message.reply_text(bot_answer, reply_markup=keyboard)
        if question_answer_state == "UNKNOWN":
            agent_id = random.choice(AGENT_IDS)
            send_telegram_message.delay(f"کاربر {message.from_user.first_name} با یوزرنیم @{message.from_user.username} و آیدی {message.from_user.id} نیاز به کمک دارد.\nسوال: {message.text}", agent_id)
    print("Starting Telegram Bot...")
    return app

def infinite_send_loop():
    app = pyrogram.Client("event", bot_token=TELEGRAM_BOT_TOKEN, api_hash=TELEGRAM_API_HASH, api_id=TELEGRAM_API_ID)
    app.start()
    while True:
        request = SendTelegramMessageRequest.objects.first()
        if not request:
            time.sleep(0.5)
            continue
        text = request.text
        user_id = request.user_id
        request.delete()
        app.send_message(user_id, text)
        time.sleep(0.5)

def get_docs_and_faq_data(request):
    docs = Document.objects.all()
    faqs = FAQ.objects.all()
    data = []
    for doc in docs:
      data.append(f"Category: {doc.category}, Sub Category: {doc.sub_category}, Solution: {doc.solution}")
    for faq in faqs:
      data.append(f"Category: {faq.category}, Question: {faq.question}, Answer: {faq.answer}")
    return "\n".join(data)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def send_alert(self, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        for user_id in UserMessage.objects.all().distinct("user_id").values_list("user_id", flat=True):
            send_telegram_message.delay(alert.text, user_id)
        logger.info(f"Successfully queued alert {alert_id} for all users")
    except Exception as e:
        logger.error(f"Failed to send alert {alert_id}: {str(e)}")
        raise self.retry(exc=e)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_telegram_message(self, message, user_id):
    SendTelegramMessageRequest.objects.create(text=message, user_id=user_id)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def analyze_incoming_messages(self):
    try:
        min_timestamp = timezone.now() - timedelta(days=1)
        questions = UserMessage.objects.filter(timestamp__gte=min_timestamp, state="UNKNOWN")
        if not questions.exists():
            return
        questions_text = "\n".join([f"Question: {question.text}" for question in questions])
        content, _ = send_request_to_endpoint([
            {
                "role": "system",
                "content": ANALYZE_INCOMING_MESSAGES_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": questions_text
            }
        ])
        TelegramSummary.objects.create(text=content)
        for agent_id in AGENT_IDS:
            send_telegram_message.delay(content, agent_id)
        logger.info("Successfully analyzed incoming messages and sent summary to agents")
    except Exception as e:
        logger.error(f"Failed to analyze incoming messages: {str(e)}")
        raise self.retry(exc=e)

@shared_task
def set_message_rate(message_id, rate):
    message = BotMessage.objects.get(id=message_id)
    message.rating = rate
    message.save()