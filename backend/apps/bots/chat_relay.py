from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class RelayResult:
    ok: bool
    error: str | None = None


class BotConnectionRegistry:
    _api_key_to_channel: dict[str, str] = {}

    @classmethod
    def bind(cls, api_key: str, channel_name: str) -> None:
        cls._api_key_to_channel[api_key] = channel_name

    @classmethod
    def unbind(cls, api_key: str, channel_name: str) -> bool:
        current = cls._api_key_to_channel.get(api_key)
        if current == channel_name:
            cls._api_key_to_channel.pop(api_key, None)
            return True
        return False

    @classmethod
    def get_channel_name(cls, api_key: str) -> str | None:
        return cls._api_key_to_channel.get(api_key)

    @classmethod
    def is_online(cls, api_key: str) -> bool:
        return api_key in cls._api_key_to_channel


class UserConnectionRegistry:
    _user_bot_to_channel: dict[str, str] = {}

    @classmethod
    def _key(cls, user_id: str, bot_id: str) -> str:
        return f'{user_id}:{bot_id}'

    @classmethod
    def bind(cls, user_id: str, bot_id: str, channel_name: str) -> str | None:
        key = cls._key(user_id, bot_id)
        previous = cls._user_bot_to_channel.get(key)
        cls._user_bot_to_channel[key] = channel_name
        return previous

    @classmethod
    def unbind(cls, user_id: str, bot_id: str, channel_name: str) -> bool:
        key = cls._key(user_id, bot_id)
        current = cls._user_bot_to_channel.get(key)
        if current == channel_name:
            cls._user_bot_to_channel.pop(key, None)
            return True
        return False


def user_group_name(user_uuid: str, bot_uuid: str) -> str:
    return f'chat_user_{user_uuid}_{bot_uuid}'


class ChatRelay:
    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    @classmethod
    async def relay_user_message(
        cls,
        *,
        consumer: Any,
        bot_api_key: str,
        user_id: str,
        content: str,
        ack_id: str,
    ) -> RelayResult:
        channel_name = BotConnectionRegistry.get_channel_name(bot_api_key)
        if not channel_name:
            return RelayResult(ok=False, error='机器人当前离线，消息无法送达')

        payload = {
            'v': 1,
            'type': 'user_message',
            'user_id': user_id,
            'content': content,
            'ack_id': ack_id,
            'timestamp': cls._timestamp(),
        }
        try:
            await consumer.channel_layer.send(
                channel_name,
                {
                    'type': 'relay.user_message',
                    'payload': payload,
                },
            )
        except Exception:
            BotConnectionRegistry.unbind(bot_api_key, channel_name)
            return RelayResult(ok=False, error='机器人当前离线，消息无法送达')
        return RelayResult(ok=True)

    @classmethod
    async def relay_bot_message(
        cls,
        *,
        consumer: Any,
        bot_id: str,
        user_id: str,
        content: str,
        timestamp: str | None,
        correlation_id: str | None,
    ) -> None:
        group = user_group_name(user_id, bot_id)
        payload: dict[str, Any] = {
            'v': 1,
            'type': 'bot_message',
            'content': content,
            'timestamp': timestamp or cls._timestamp(),
        }
        if correlation_id:
            payload['correlation_id'] = correlation_id

        await consumer.channel_layer.group_send(
            group,
            {
                'type': 'relay.bot_message',
                'payload': payload,
            },
        )
