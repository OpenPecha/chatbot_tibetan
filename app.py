import os
import time
import uuid
from typing import Dict, List, Tuple

import gradio as gr
import requests

from store import store_message_pair

# Environment Variables
DEBUG = bool(os.getenv("DEBUG", False))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BING_TRANSLATE_API_KEY = os.getenv("BING_TRANSLATE_API_KEY")

# Type Definitions
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
CHATGPT_MSG = Dict[str, str]  # {"role": "user|assistant", "content": "text"}
CHATGPT_HISTROY = List[CHATGPT_MSG]
CHATBOT_MSG = Tuple[str, str]  # (user_message, bot_response)
CHATBOT_HISTORY = List[CHATBOT_MSG]

# Constants
LANG_BO = "bo"
LANG_ZH = "en"


def bing_translate(text: str, from_lang: str, to_lang: str):
    if DEBUG:
        if from_lang != "bo":
            return "ཀཀཀཀཀཀ"
        return "aaaaa"
    headers = {
        "Ocp-Apim-Subscription-Key": BING_TRANSLATE_API_KEY,
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Region": "eastus",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    resp = requests.post(
        url="https://api.cognitive.microsofttranslator.com/translate",
        params={"api-version": "3.0", "from": from_lang, "to": to_lang},
        json=[{"text": text}],
        headers=headers,
    )
    result = resp.json()
    if resp.status_code == 200:
        return result[0]["translations"][0]["text"]
    else:
        raise Exception("Error in translation API: ", result)


def make_completion(history):
    if DEBUG:
        time.sleep(2)
        return "aaaaa"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    resp = requests.post(
        url="https://api.openai.com/v1/chat/completions",
        json={"model": "gpt-3.5-turbo", "messages": history},
        headers=headers,
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        print(resp.content)
        return "Sorry, I don't understand."


def user(input_bo: str, history_bo: list):
    history_bo.append([input_bo, None])
    return "", history_bo


def store_chat(chat_id: str, history_bo: list, history_zh):
    bo_msg_pair = history_bo[-1]
    store_message_pair(chat_id, bo_msg_pair, LANG_BO)
    en_msg_pair = (history_zh[-1]["content"], history_zh[-2]["content"])
    store_message_pair(chat_id, en_msg_pair, LANG_ZH)


def bot(history_bo: list, history_en: list, request: gr.Request):
    """Translate user input to English, send to OpenAI, translate response to Tibetan, and return to user.

    Args:
        input_bo (str): Tibetan input from user
        history_bo (CHATBOT_HISTORY): Tibetan history of gradio chatbot
        history_en (CHATGPT_HISTORY): English history of OpenAI ChatGPT

    Returns:
        history_bo (CHATBOT_HISTORY): Tibetan history of gradio chatbot
        history_en (CHATGPT_HISTORY): English history of OpenAI ChatGPT
    """
    input_bo = history_bo[-1][0]
    input_en = bing_translate(input_bo, LANG_BO, LANG_ZH)
    history_en.append({"role": ROLE_USER, "content": input_en})
    response_en = make_completion(history_en)
    resopnse_bo = bing_translate(response_en, LANG_ZH, LANG_BO)
    history_en.append({"role": ROLE_ASSISTANT, "content": response_en})
    history_bo[-1][1] = resopnse_bo
    if DEBUG:
        print("------------------------")
        print(history_bo)
        print(history_en)
        print("------------------------")

    store_chat(
        chat_id=request.client.host, history_bo=history_bo, history_zh=history_en
    )
    return history_bo, history_en


with gr.Blocks() as demo:
    history_en = gr.State(value=[])
    history_bo = gr.Chatbot(label="Tibetan Chatbot").style(height=650)
    input_bo = gr.Textbox(
        show_label=False, placeholder="Type a message here and press enter"
    )
    input_bo.submit(
        fn=user,
        inputs=[input_bo, history_bo],
        outputs=[input_bo, history_bo],
        queue=False,
    ).then(
        fn=bot,
        inputs=[history_bo, history_en],
        outputs=[history_bo, history_en],
    )

    clear = gr.Button("New Chat")
    clear.click(lambda: None, None, history_bo, queue=False)

demo.launch()
