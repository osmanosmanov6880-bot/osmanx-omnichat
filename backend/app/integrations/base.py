"""Uniform adapter contract. Explicit capabilities, no fabricated success."""
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass
class Capabilities:
    send_text: bool = True
    receive_text: bool = True
    attachments: bool = False
    history_sync: bool = False
    templates: bool = False
    requires_customer_window: bool = False

class AdapterError(Exception):
    def __init__(self, message, retriable=False, uncertain=False, rate_limited=False, retry_after=None):
        super().__init__(message)
        self.retriable = retriable
        # A provider may have accepted a POST before connection failure/timeout.
        # Reconciliation is required before any manual resend.
        self.uncertain = uncertain
        self.rate_limited = rate_limited
        self.retry_after = retry_after

class ChannelAdapter(Protocol):
    provider: str
    async def connect(self, credentials: dict) -> dict: ...
    def get_capabilities(self) -> Capabilities: ...
    async def validate_credentials(self, credentials: dict) -> dict: ...
    async def send_message(self, credentials: dict, channel, conversation, text: str, message_id: str | None = None) -> str: ...
    async def get_conversations(self, credentials: dict) -> list: ...
    async def get_messages(self, credentials: dict, chat_id: str) -> list: ...
    async def receive_messages(self, payload: dict) -> list: ...
    async def refresh_credentials(self, credentials: dict) -> dict: ...
    async def disconnect(self, credentials: dict) -> None: ...
