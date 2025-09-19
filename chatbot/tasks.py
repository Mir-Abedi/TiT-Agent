import requests
from django.conf import settings
import typing
import json

class PreviousMessage(typing.TypedDict):
    role: typing.Literal[0, 1, 2] # 0 for system prompt, 1 for user prompt, 2 for assistant
    text: str


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

    payload = json.dumps({
        "model": API_MODEL,
        "messages": model_messages,
        "max_tokens": 2000,
        "temperature": 0.7
    })
    headers = {
        'authorization': f'apikey {API_KEY}',
    }

    response = requests.request("POST", API_ENDPOINT, headers=headers, data=payload)

    return response.json()["choices"][0]["message"]["content"]


