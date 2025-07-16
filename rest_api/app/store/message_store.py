import uuid
import datetime
from typing import List, Dict


class MessageStore:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not MessageStore._initialized:
            self.messages: List[Dict] = []
            MessageStore._initialized = True

    def add_message(self, message: str, producer_id: str) -> str:
        message_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        self.messages.append(
            {"message_id": message_id, "message": message, "producer_id": producer_id, "timestamp": timestamp}
        )
        return message_id

    def get_messages(self, max_count: int = 10) -> List[Dict]:
        return self.messages[-max_count:][::-1]
