import os
from typing import Tuple

import openai


class ChatGpt:
    def __init__(self, api_key, max_tokens=4096):
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.message_history = []
        self.total_tokens = 0

        # Set up the OpenAI API client
        openai.api_key = self.api_key

    def add_message(self, role: str, content: str):
        self.message_history.append({"role": role, "content": content})
        self._truncate_history()

    def add_system_message(self, content: str):
        self.add_message("system", content)

    def generate_response(self, user_input: str) -> str:
        self.add_message("user", user_input)
        response = self._call_openai_api(self.message_history)
        self.add_message("assistant", response)

        return response

    def _truncate_history(self):
        while self.total_tokens > self.max_tokens:
            if self.message_history[0]["role"] != "system":
                self.message_history.pop(0)
            else:
                break

    def _call_openai_api(self, messages) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        self.total_tokens += response["usage"]["total_tokens"]
        return response["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    chat = ChatGpt(os.getenv("OPENAI_API_KEY"))

    chat.add_system_message("The assistant can answer questions and tell jokes.")
    user_input = "Tell me a joke."
    user_msg, bot_response = chat.generate_response(user_input)
    assert user_msg == user_input
    print("User:", user_msg)
    print("Assistant:", bot_response)
    print("Total Tokens:", chat.total_tokens)

    user_input = "another one"
    user_msg, bot_response = chat.generate_response(user_input)
    assert user_msg == user_input
    print("User:", user_msg)
    print("Assistant:", bot_response)
    print("Total Tokens:", chat.total_tokens)
