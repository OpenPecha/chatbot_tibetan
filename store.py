import json
import uuid
from datetime import datetime
from typing import Tuple

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
all_chats_table = dynamodb.Table("ChatbotTibetanAllChats")


def store_message_pair(chat_id: str, msg_pair: Tuple[str, str], lang: str):
    """Store the chat history to DynamoDB

    Args:
        chat_id: The ID of the chat
        msg_pair: tuple with 2 items (user_message, bot_response)
        lang: The language of the msg_pair
        order: The order of the msg_pair in chat history
    """

    # Add the new message to the chat history
    msg_pair_id = uuid.uuid4().hex[:10]
    response = all_chats_table.put_item(
        Item={
            "msg_pair_id": msg_pair_id,
            "msg_pair": json.dumps(msg_pair, ensure_ascii=False),
            "lang": lang,
            "created_at": datetime.now().isoformat(),
            "chat_id": chat_id,
        }
    )
    return response


if __name__ == "__main__":
    # Replace with your own DynamoDB table name and chat ID
    chat_id = uuid.uuid4().hex[:4]

    # Replace with your own chat history (list of tuples or list of dictionaries)
    chat_history = [
        ("User", "Hello, how are you?"),
        ("Chatbot", "I am fine, thank you!"),
    ]
    for msg_pair in chat_history:
        store_message_pair(chat_id, msg_pair, "en")
