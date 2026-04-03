"""WebSocket 测试 Fixture"""
import pytest
import secrets
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.conf import settings
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken

from apps.bots.consumers import BotGatewayConsumer, UserChatConsumer
from apps.bots.models import Bot


# 创建带路由的应用
user_chat_app = URLRouter([
    path('ws/chat/<uuid:bot_id>/', UserChatConsumer.as_asgi()),
])

bot_gateway_app = URLRouter([
    path('ws/bot/', BotGatewayConsumer.as_asgi()),
])


@pytest.fixture
def bot(db, user):
    """创建一个测试用的 Bot"""
    return Bot.objects.create(
        bot_id='123456789',
        nickname='TestBot',
        master=user,
        master_qq='987654321',
        api_key=secrets.token_hex(32),
        status='online',
    )


@pytest.fixture
def channel_layer():
    """确保使用内存 channel layer"""
    from channels.layers import InMemoryChannelLayer
    return InMemoryChannelLayer()


@pytest.fixture
def bot_ws_communicator(channel_layer, bot):
    """
    创建已认证的 Bot WebSocket Communicator

    返回一个已经发送 auth 帧并成功认证的 communicator
    """
    async def _create():
        communicator = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        # 注入 channel layer
        communicator.instance.channel_layer = channel_layer
        connected, _ = await communicator.connect()
        assert connected, "Bot WebSocket 连接失败"

        # 发送认证帧
        await communicator.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": bot.api_key,
        })

        # 等待一小段时间确保认证完成
        # Bot 认证成功后不会发送消息，只是保持连接
        # 这里我们可以通过检查 Registry 来确认
        from apps.bots.chat_relay import BotConnectionRegistry
        assert BotConnectionRegistry.is_online(bot.api_key), "Bot 认证失败"

        return communicator
    return _create


@pytest.fixture
def user_ws_communicator(channel_layer, user, bot):
    """
    创建已认证的 User WebSocket Communicator

    返回一个已经连接并接受的 communicator
    """
    async def _create():
        # 生成 JWT token
        token = AccessToken.for_user(user)

        communicator = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        # 注入 channel layer
        communicator.instance.channel_layer = channel_layer
        connected, _ = await communicator.connect()
        assert connected, "User WebSocket 连接失败"

        return communicator
    return _create


@pytest.fixture
def unauthenticated_user_communicator(channel_layer, bot):
    """创建未认证的 User WebSocket Communicator（用于测试认证失败）"""
    async def _create(token=""):
        url = f"/ws/chat/{bot.id}/"
        if token:
            url += f"?token={token}"

        communicator = WebsocketCommunicator(
            user_chat_app,
            url,
        )
        communicator.instance.channel_layer = channel_layer
        return communicator
    return _create


@pytest.fixture
def unauthenticated_bot_communicator(channel_layer):
    """创建未认证的 Bot WebSocket Communicator（用于测试认证失败）"""
    async def _create():
        communicator = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        communicator.instance.channel_layer = channel_layer
        connected, _ = await communicator.connect()
        assert connected, "Bot WebSocket 连接失败"
        return communicator
    return _create
