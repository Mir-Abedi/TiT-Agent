import requests
from django.conf import settings
import typing
import json
from django.utils import timezone
from datetime import timedelta
from telegram.models import UserMessage


class Message(typing.TypedDict):
    role: typing.Literal["assistant", "user", "system"]
    content: str

API_KEY = settings.OPENAI_API_KEY
API_ENDPOINT = settings.OPENAI_ENDPOINT
API_MODEL = settings.API_MODEL

def get_history_messages(user_id, chat_id, max_num_user_messages=10):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    messages = UserMessage.objects.filter(timestamp__gte=one_hour_ago, user_id=user_id, chat_id=chat_id, bot_message__isnull=False)
    user_messages_count = messages.count()
    previous_messages = []
    for message in messages[min(0, user_messages_count - max_num_user_messages):]:
        previous_messages.extend(
            [
                Message(
                    role="user",
                    content=message.text
                ),
                Message(
                    role="assistant",
                    content=message.bot_message.text
                )
            ]
        )
    return previous_messages

def get_llm_answer(user, system="", previous_messages:list[Message]=[]):
    # If system prompt is available skip previous_messages where role is system
    # Find from previous_messages if is not given
    if not system:
        system_messages = [i for i in previous_messages if i.role == "system"]
        if system_messages:
            system = system_messages[-1].text
    # Filter messages where message is not system
    filtered_messages = [i for i in previous_messages if i.role != "system"]
    model_messages = []
    if system:
        model_messages.append(
            Message(
                role="system",
                content=system
            )
        )
    model_messages.extend(filtered_messages)
    model_messages.append(
        Message(
            role="user",
            content=user
        )
    )

    ans, is_okay = send_request_to_endpoint(model_messages)
    if not is_okay:
        return "خطا در پردازش پیام"
    return ans

def send_request_to_endpoint(messages: list[Message]):
    url = API_ENDPOINT

    payload = json.dumps({
        "model": API_MODEL,
        "messages": messages,
        "max_tokens": 3000,
        "temperature": 0.7
    })
    headers = {
        'Authorization': 'apikey bf9c0ae0-3a2c-5eee-9cd9-cca7ae809836',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    ans = response.json()
    is_okay = True
    if ans.get("prompt_filter_results", []):
        prompt_filter_results = ans["prompt_filter_results"][0]
        for i in prompt_filter_results.get("content_filter_results", {}):
            if prompt_filter_results["content_filter_results"][i]["filtered"]:
                is_okay = False
                break

    return ans["choices"][0]["message"]["content"], is_okay
