import os
import uuid
from typing import Dict, List, Optional, Tuple

import gradio as gr
import requests

from chat import ChatGpt
from store import store_message_pair

# Environment Variables
DEBUG = bool(os.getenv("DEBUG", False))
VERBOSE = bool(os.getenv("V", False))
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
LANG_MEDIUM = "en"

chatbot = ChatGpt(OPENAI_API_KEY)


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


def user(input_bo: str, history_bo: list):
    history_bo.append([input_bo, None])
    return "", history_bo


def store_chat(
    chat_id: str,
    msg_pair_bo: Tuple[str, str],
    msg_pair_medium: Tuple[str, str],
    medium_lang: str,
):
    msg_pair = {
        "bo": msg_pair_bo,
        medium_lang: msg_pair_medium,
    }
    store_message_pair(chat_id, msg_pair)


def bot(history_bo: list, chat_id: str):
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
    input_ = bing_translate(input_bo, LANG_BO, LANG_MEDIUM)
    response = chatbot.generate_response(input_)
    resopnse_bo = bing_translate(response, LANG_MEDIUM, LANG_BO)
    history_bo[-1][1] = resopnse_bo
    if VERBOSE:
        print("------------------------")
        print(history_bo)
        print(history_en)
        print("------------------------")

    store_chat(
        chat_id=chat_id,
        msg_pair_bo=(input_bo, resopnse_bo),
        msg_pair_medium=(input_, response),
        medium_lang=LANG_MEDIUM,
    )
    return history_bo


def get_chat_id():
    chatbot.clear_history()
    return str(uuid.uuid4())


with gr.Blocks() as demo:
    chat_id = gr.State(value=get_chat_id)
    history_en = gr.State(value=[])
    history_bo = gr.Chatbot(label="Tibetan Chatbot").style(height=650)
    input_bo = gr.Textbox(
        show_label=False,
        placeholder=f"Type a message here and press enter",
    )
    input_bo.submit(
        fn=user,
        inputs=[input_bo, history_bo],
        outputs=[input_bo, history_bo],
        queue=False,
    ).then(
        fn=bot,
        inputs=[history_bo, chat_id],
        outputs=[history_bo],
    )

    clear = gr.Button("New Chat")
    clear.click(lambda: [], None, history_bo, queue=False)

demo.launch()
