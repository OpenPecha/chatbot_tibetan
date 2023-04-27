import json
import uuid
from datetime import datetime
from typing import Dict, Tuple

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
all_chats_table = dynamodb.Table("ChatbotTibetanAllChats")


def store_message_pair(chat_id: str, msg_pair: Dict[str, Tuple[str, str]]):
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
            "created_at": datetime.now().isoformat(),
            "chat_id": chat_id,
        }
    )
    return response


if __name__ == "__main__":
    # Replace with your own DynamoDB table name and chat ID
    chat_id = str(uuid.uuid4())

    # Replace with your own chat history (list of tuples or list of dictionaries)
    msg_pair = {"bo": ("hello", "hello"), "en": ("hello", "hello")}
    response = store_message_pair(chat_id, msg_pair)
    print(response)
