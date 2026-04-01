import json
import time
from collections import deque
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.bots.chat_relay import BotConnectionRegistry, ChatRelay, UserConnectionRegistry, user_group_name
from apps.bots.models import Bot
from apps.users.models import User


class UserChatConsumer(AsyncJsonWebsocketConsumer):
    RATE_LIMIT_WINDOW_SECONDS = 5
    RATE_LIMIT_MAX_MESSAGES = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.bot = None
        self.group_name = ''
        self._message_timestamps: deque[float] = deque()

    async def connect(self):
        token = self._extract_token_from_query()
        user = await self._resolve_user_from_token(token)
        bot_id = str(self.scope['url_route']['kwargs'].get('bot_id', ''))
        bot = await self._get_bot(bot_id)

        if not user or not bot:
            await self.close(code=4401)
            return

        self.user = user
        self.bot = bot
        self.group_name = user_group_name(str(self.user.id), str(self.bot.id))
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        previous_channel = UserConnectionRegistry.bind(str(self.user.id), str(self.bot.id), self.channel_name)
        if previous_channel and previous_channel != self.channel_name:
            try:
                await self.channel_layer.send(
                    previous_channel,
                    {
                        'type': 'relay.force_disconnect',
                        'payload': {
                            'v': 1,
                            'type': 'system',
                            'content': '聊天已在其他窗口打开，请前往新窗口继续',
                            'code': 'FORCE_DISCONNECT',
                        },
                    },
                )
            except Exception:
                pass

        if not BotConnectionRegistry.is_online(self.bot.api_key):
            await self._send_system('机器人当前离线，消息无法送达')

    async def disconnect(self, code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if self.user and self.bot:
            UserConnectionRegistry.unbind(str(self.user.id), str(self.bot.id), self.channel_name)

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type != 'message':
            return

        ack_id = str(content.get('ack_id', '')).strip()
        message_content = str(content.get('content', '')).strip()
        if not ack_id or not message_content:
            await self._send_ack(ack_id, 'error', '消息格式错误')
            return

        if self._is_rate_limited():
            await self._send_ack(ack_id, 'error', '发送过于频繁，请稍后再试')
            return

        relay_result = await ChatRelay.relay_user_message(
            consumer=self,
            bot_api_key=self.bot.api_key,
            user_id=str(self.user.id),
            content=message_content,
            ack_id=ack_id,
        )
        if relay_result.ok:
            await self._send_ack(ack_id, 'ok')
            return

        await self._send_ack(ack_id, 'error', relay_result.error or '消息发送失败')
        await self._send_system(relay_result.error or '机器人当前离线，消息无法送达')

    async def relay_bot_message(self, event):
        await self.send_json(event['payload'])

    async def relay_force_disconnect(self, event):
        await self.send_json(event['payload'])
        await self.close(code=4001)

    def _current_time(self) -> float:
        return time.monotonic()

    def _is_rate_limited(self) -> bool:
        now = self._current_time()
        while self._message_timestamps and (now - self._message_timestamps[0]) > self.RATE_LIMIT_WINDOW_SECONDS:
            self._message_timestamps.popleft()

        if len(self._message_timestamps) >= self.RATE_LIMIT_MAX_MESSAGES:
            return True

        self._message_timestamps.append(now)
        return False

    async def _send_ack(self, ack_id: str, status: str, error: str | None = None):
        payload = {
            'v': 1,
            'type': 'ack',
            'ack_id': ack_id,
            'status': status,
            'error': error,
        }
        await self.send_json(payload)

    async def _send_system(self, content: str):
        await self.send_json(
            {
                'v': 1,
                'type': 'system',
                'content': content,
            }
        )

    def _extract_token_from_query(self) -> str:
        query = self.scope.get('query_string', b'').decode('utf-8')
        query_dict = parse_qs(query)
        token_values = query_dict.get('token') or []
        return token_values[0] if token_values else ''

    @database_sync_to_async
    def _resolve_user_from_token(self, token: str):
        if not token:
            return None

        try:
            access = AccessToken(token)
        except (InvalidToken, TokenError):
            return None

        user_id = str(access.get('user_id', ''))
        if not user_id:
            return None

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_bot(self, bot_id: str):
        try:
            return Bot.objects.get(id=bot_id)
        except Bot.DoesNotExist:
            return None


class BotGatewayConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = None
        self.api_key = ''
        self.authenticated = False

    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        if self.authenticated and self.api_key:
            removed = BotConnectionRegistry.unbind(self.api_key, self.channel_name)
            if removed:
                await self._update_bot_offline()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data is not None:
            return
        if text_data is None:
            return

        try:
            content = json.loads(text_data)
        except json.JSONDecodeError:
            await self.close(code=4400)
            return

        message_type = content.get('type')
        if not self.authenticated:
            await self._handle_auth(content)
            return

        if message_type == 'bot_message':
            await self._handle_bot_message(content)
            return

    async def relay_user_message(self, event):
        if not self.authenticated:
            return
        await self.send_json(event['payload'])

    async def _handle_auth(self, content: dict):
        if content.get('type') != 'auth' or str(content.get('api_key', '')).strip() == '':
            await self.close(code=4401)
            return
        if int(content.get('v', 1)) != 1:
            await self.close(code=4401)
            return

        api_key = str(content.get('api_key')).strip()
        bot = await self._get_bot_by_api_key(api_key)
        if not bot:
            await self.close(code=4401)
            return

        self.bot = bot
        self.api_key = api_key
        self.authenticated = True
        BotConnectionRegistry.bind(api_key, self.channel_name)
        await self._update_bot_online()

    async def _handle_bot_message(self, content: dict):
        user_id = str(content.get('user_id', '')).strip()
        message_content = str(content.get('content', '')).strip()
        if not user_id or not message_content:
            return

        correlation_id = content.get('correlation_id')
        timestamp = content.get('timestamp')
        await ChatRelay.relay_bot_message(
            consumer=self,
            bot_id=str(self.bot.id),
            user_id=user_id,
            content=message_content,
            timestamp=timestamp,
            correlation_id=str(correlation_id) if correlation_id else None,
        )

    @database_sync_to_async
    def _get_bot_by_api_key(self, api_key: str):
        try:
            return Bot.objects.get(api_key=api_key)
        except Bot.DoesNotExist:
            return None

    @database_sync_to_async
    def _update_bot_online(self):
        """WebSocket 连接成功时更新 Bot 为在线状态"""
        try:
            self.bot.status = 'online'
            self.bot.last_seen = timezone.now()
            self.bot.save(update_fields=['status', 'last_seen'])
        except Exception:
            pass

    @database_sync_to_async
    def _update_bot_offline(self):
        """WebSocket 断开时更新 Bot 为离线状态"""
        try:
            bot = Bot.objects.get(api_key=self.api_key)
            bot.status = 'offline'
            bot.save(update_fields=['status'])
        except Bot.DoesNotExist:
            pass
