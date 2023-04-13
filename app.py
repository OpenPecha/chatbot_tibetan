import os
import random
import time
from typing import Dict

import gradio as gr

API_KEY = os.getenv("OPENAI_API_KEY")

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
HISTROY = Dict[str, str]  # {"role": "user|assistant", "content": "text"}


def user(user_message, history):
    return "", history + [[user_message, None]]


def bot(history):
    bot_message = random.choice(["Yes", "No"])
    history[-1][1] = bot_message
    time.sleep(1)
    return history


with gr.Blocks() as demo:
    history = gr.Chatbot(label="Tibetan Chatbot").style(height=750)

    msg = gr.Textbox(
        show_label=False, placeholder="Type a message here and press enter"
    )
    msg.submit(user, [msg, history], [msg, history], queue=False).then(
        bot, history, history
    )

    clear = gr.Button("New Chat")
    clear.click(lambda: None, None, history, queue=False)

demo.launch()
