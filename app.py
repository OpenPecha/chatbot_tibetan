import os
from typing import Dict, List

import gradio as gr
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
HISTROY = List[Dict[str, str]]  # [{"role": "user|assistant", "content": "text"},...]


def make_completion(history):
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


def user(user_message: str, history: list):
    return "", history + [[user_message, None]]


def bot(input: str, history: list):
    history.append({"role": ROLE_USER, "content": input})
    response = make_completion(history)
    history.append({"role": ROLE_ASSISTANT, "content": response})
    messages = [
        (history[i]["content"], history[i + 1]["content"])
        for i in range(0, len(history) - 1, 2)
    ]
    return messages, history, ""


with gr.Blocks() as demo:
    history = gr.State(value=[])
    chatbot = gr.Chatbot(label="Tibetan Chatbot").style(height=750)
    msg = gr.Textbox(
        show_label=False, placeholder="Type a message here and press enter"
    )
    msg.submit(
        fn=bot, inputs=[msg, history], outputs=[chatbot, history, msg], queue=False
    )

    clear = gr.Button("New Chat")
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()
