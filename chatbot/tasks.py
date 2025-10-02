import requests
from django.conf import settings
import typing
import json

class PreviousMessage(typing.TypedDict):
    role: typing.Literal[0, 1, 2] # 0 for system prompt, 1 for user prompt, 2 for assistant
    text: str


class Message(typing.TypedDict):
    role: typing.Literal["assistant", "user", "system"]
    content: str

API_KEY = settings.OPENAI_API_KEY
API_ENDPOINT = settings.OPENAI_ENDPOINT
API_MODEL = settings.API_MODEL

def get_llm_answer(user, system="", previous_messages:list[PreviousMessage]=[]):
    # If system prompt is available skip previous_messages where role is system
    # Find from previous_messages if is not given
    if not system:
        system_messages = [i for i in previous_messages if i.role == 0]
        if system_messages:
            system = system_messages[-1].text
    # Filter messages where message is not system
    filtered_messages = [i for i in previous_messages if i.role != 0][-4:]
    model_messages = []
    if system:
        model_messages.append(
            {
                "role": "system",
                "content": system
            }
        )
    for i in filtered_messages:
        model_messages.append(
            {
                "role": "assistant" if i.role == 2 else "user",
                "content": i.text
            }
        )
    model_messages.append(
        {
            "role": "user",
            "content": user
        }
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
            if prompt_filter_results[i]["filtered"]:
                is_okay = False
                break

    return ans["choices"][0]["message"]["content"], is_okay
