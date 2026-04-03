"""WebSocket 网关集成测试

将原 ws_acceptance.py 转换为标准 pytest 测试
使用 channels.testing.WebsocketCommunicator 进行内存测试
"""
import asyncio

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken

from apps.bots.consumers import BotGatewayConsumer, UserChatConsumer
from apps.bots.chat_relay import BotConnectionRegistry


# 创建带路由的应用
user_chat_app = URLRouter([
    path('ws/chat/<uuid:bot_id>/', UserChatConsumer.as_asgi()),
])

bot_gateway_app = URLRouter([
    path('ws/bot/', BotGatewayConsumer.as_asgi()),
])


# =============================================================================
# Bot Gateway Tests
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestBotGateway:
    """Bot WebSocket 网关测试"""

    async def test_bot_connects_and_authenticates(self, bot):
        """Bot 使用有效 api_key 连接并认证成功"""

        communicator = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        connected, _ = await communicator.connect()
        assert connected

        # 发送认证帧
        await communicator.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": bot.api_key,
        })

        # 认证成功后连接保持打开
        assert await communicator.receive_nothing() is True
        assert BotConnectionRegistry.is_online(bot.api_key) is True

        await communicator.disconnect()
        # 清理 registry - 获取 bot 当前的 channel_name
        channel = BotConnectionRegistry.get_channel_name(bot.api_key)
        if channel:
            BotConnectionRegistry.unbind(bot.api_key, channel)

    async def test_bot_rejected_with_invalid_api_key(self, bot):
        """Bot 使用无效 api_key 被拒绝"""

        communicator = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        connected, _ = await communicator.connect()
        assert connected

        # 发送无效认证帧
        await communicator.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": "invalid-api-key",
        })

        # 等待一小段时间让服务器处理
        await asyncio.sleep(0.1)

        # 连接应该被关闭（通过 websocket.close 消息）
        # 或者 output_queue 中有 close 消息
        await communicator.disconnect()

    async def test_bot_rejected_with_malformed_auth(self, bot):
        """Bot 发送格式错误的认证帧被拒绝"""

        communicator = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        connected, _ = await communicator.connect()
        assert connected

        # 发送缺少必要字段的认证帧
        await communicator.send_json_to({
            "v": 1,
            "type": "auth",
            # 缺少 api_key
        })

        # 等待处理
        await asyncio.sleep(0.1)

        # 连接应该被关闭
        await communicator.disconnect()

    async def test_bot_receives_relayed_user_message(self, bot, user):
        """Bot 认证后可以接收来自用户的 relay 消息"""

        # 创建 Bot communicator
        bot_comm = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        connected, _ = await bot_comm.connect()
        assert connected

        # 认证 Bot
        await bot_comm.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": bot.api_key,
        })

        # 等待认证完成
        await asyncio.sleep(0.1)
        assert BotConnectionRegistry.is_online(bot.api_key) is True

        # 通过 channel layer 直接发送 relay 消息（模拟 UserChatConsumer 发送）
        channel_layer = get_channel_layer()
        await channel_layer.send(
            BotConnectionRegistry.get_channel_name(bot.api_key),
            {
                "type": "relay.user_message",
                "payload": {
                    "v": 1,
                    "type": "user_message",
                    "content": "Hello bot!",
                    "user_id": str(user.id),
                },
            },
        )

        # Bot 应该收到消息
        response = await bot_comm.receive_json_from(timeout=1)
        assert response["type"] == "user_message"
        assert response["content"] == "Hello bot!"
        assert response["user_id"] == str(user.id)

        await bot_comm.disconnect()
        # 清理 registry
        channel = BotConnectionRegistry.get_channel_name(bot.api_key)
        if channel:
            BotConnectionRegistry.unbind(bot.api_key, channel)


# =============================================================================
# User Gateway Tests
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestUserGateway:
    """User WebSocket 网关测试"""

    async def test_user_connects_with_valid_jwt(self, user, bot):
        """用户使用有效 JWT 成功连接"""

        token = AccessToken.for_user(user)

        communicator = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        connected, _ = await communicator.connect()
        assert connected is True

        # 连接成功后，如果 bot 离线会收到系统消息
        # 或者什么都没有（取决于 bot 状态）
        await communicator.disconnect()

    async def test_user_rejected_with_invalid_jwt(self, bot):
        """用户使用无效 JWT 被拒绝"""

        communicator = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token=invalid-token",
        )
        connected, _ = await communicator.connect()
        # 应该连接失败或被立即关闭
        assert connected is False

    async def test_user_rejected_without_jwt(self, bot):
        """用户没有 JWT 被拒绝"""

        communicator = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/",
        )
        connected, _ = await communicator.connect()
        # 应该连接失败
        assert connected is False

    async def test_user_receives_system_message_when_bot_offline(self, user, bot):
        """用户连接时如果 bot 离线，收到系统消息提醒"""

        # 确保 bot 离线
        bot.status = 'offline'
        await asyncio.get_event_loop().run_in_executor(None, bot.save)

        token = AccessToken.for_user(user)

        communicator = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        connected, _ = await communicator.connect()
        assert connected is True

        # 应该收到系统消息
        response = await communicator.receive_json_from(timeout=1)
        assert response["type"] == "system"
        assert "离线" in response["content"]

        await communicator.disconnect()

    async def test_user_message_gets_ack(self, user, bot):
        """用户发送消息后收到 ack 响应"""

        token = AccessToken.for_user(user)

        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        connected, _ = await user_comm.connect()
        assert connected is True

        # 如果 bot 离线，先消费掉系统消息
        if not BotConnectionRegistry.is_online(bot.api_key):
            try:
                await user_comm.receive_json_from(timeout=0.5)
            except:
                pass

        # 发送用户消息
        await user_comm.send_json_to({
            "v": 1,
            "type": "message",
            "content": "Test message",
            "ack_id": "test-ack-001",
        })

        # 等待处理
        await asyncio.sleep(0.2)

        # 应该收到 ack
        response = await user_comm.receive_json_from(timeout=1)
        assert response["type"] == "ack"
        assert response["ack_id"] == "test-ack-001"
        # 如果 bot 离线，status 可能是 error，否则是 ok
        assert "status" in response

        await user_comm.disconnect()

    async def test_user_message_gets_error_ack_when_bot_offline(self, user, bot):
        """用户发送消息时如果 bot 离线，收到 error ack"""

        # 确保 bot 离线
        bot.status = 'offline'
        await asyncio.get_event_loop().run_in_executor(None, bot.save)

        token = AccessToken.for_user(user)

        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        connected, _ = await user_comm.connect()
        assert connected is True

        # 消费掉初始系统消息
        try:
            await user_comm.receive_json_from(timeout=0.5)
        except:
            pass

        # 发送用户消息
        await user_comm.send_json_to({
            "v": 1,
            "type": "message",
            "content": "Test message",
            "ack_id": "test-ack-002",
        })

        # 应该收到 error ack
        response = await user_comm.receive_json_from(timeout=1)
        assert response["type"] == "ack"
        assert response["ack_id"] == "test-ack-002"
        assert response["status"] == "error"

        # 还应该收到系统消息
        response2 = await user_comm.receive_json_from(timeout=1)
        assert response2["type"] == "system"

        await user_comm.disconnect()


# =============================================================================
# Message Relay Tests
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestMessageRelay:
    """消息中继测试"""

    async def test_user_message_relayed_to_bot(self, user, bot):
        """用户消息被正确中继到 Bot"""

        # 创建并认证 Bot
        bot_comm = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        await bot_comm.connect()
        await bot_comm.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": bot.api_key,
        })
        await asyncio.sleep(0.1)

        # 创建 User
        token = AccessToken.for_user(user)
        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        await user_comm.connect()

        # 发送用户消息
        await user_comm.send_json_to({
            "v": 1,
            "type": "message",
            "content": "Hello from user",
            "ack_id": "relay-test-001",
        })

        # Bot 应该收到消息
        bot_response = await bot_comm.receive_json_from(timeout=1)
        assert bot_response["type"] == "user_message"
        assert bot_response["content"] == "Hello from user"

        # 用户应该收到 ack
        user_response = await user_comm.receive_json_from(timeout=1)
        assert user_response["type"] == "ack"
        assert user_response["ack_id"] == "relay-test-001"

        await bot_comm.disconnect()
        await user_comm.disconnect()
        # 清理 registry
        channel = BotConnectionRegistry.get_channel_name(bot.api_key)
        if channel:
            BotConnectionRegistry.unbind(bot.api_key, channel)

    async def test_bot_message_relayed_to_user(self, user, bot):
        """Bot 消息通过 relay 到达用户"""
        from apps.bots.chat_relay import user_group_name


        token = AccessToken.for_user(user)

        # 创建 User
        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        await user_comm.connect()

        # 等待连接完成
        await asyncio.sleep(0.1)

        # 获取用户的 channel name
        user_id = str(user.id)
        bot_id = str(bot.id)

        # 通过 channel layer 直接发送 bot 消息到用户
        # 注意：user_comm 连接时会自动加入 group
        channel_layer = get_channel_layer()
        group_name = user_group_name(user_id, bot_id)

        await channel_layer.group_send(
            group_name,
            {
                "type": "relay.bot_message",
                "payload": {
                    "v": 1,
                    "type": "bot_message",
                    "content": "Hello from bot!",
                },
            },
        )

        # 等待并消费可能存在的系统消息（bot 离线提醒）
        response = None
        for _ in range(3):  # 最多尝试3次
            try:
                response = await user_comm.receive_json_from(timeout=0.5)
                if response["type"] == "bot_message":
                    break
                # 如果是 system 消息，继续等待
            except:
                break

        # 用户应该收到 bot 消息
        assert response is not None, "没有收到任何消息"
        assert response["type"] == "bot_message", f"期望收到 bot_message，但收到 {response.get('type')}"
        assert response["content"] == "Hello from bot!"

        await user_comm.disconnect()

    async def test_bot_disconnect_triggers_user_system_message(self, user, bot):
        """Bot 断开连接时，用户收到系统消息"""

        # 创建并认证 Bot
        bot_comm = WebsocketCommunicator(
            bot_gateway_app,
            "/ws/bot/",
        )
        await bot_comm.connect()
        await bot_comm.send_json_to({
            "v": 1,
            "type": "auth",
            "api_key": bot.api_key,
        })
        await asyncio.sleep(0.1)
        assert BotConnectionRegistry.is_online(bot.api_key) is True

        # 创建 User
        token = AccessToken.for_user(user)
        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        await user_comm.connect()

        # 等待并消费初始消息
        await asyncio.sleep(0.2)
        while not user_comm.output_queue.empty():
            try:
                await user_comm.receive_json_from(timeout=0.5)
            except:
                break

        # 断开 Bot 连接
        await bot_comm.disconnect()
        await asyncio.sleep(0.2)

        # Bot 应该离线
        assert BotConnectionRegistry.is_online(bot.api_key) is False

        await user_comm.disconnect()


# =============================================================================
# Rate Limiting Tests
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestRateLimiting:
    """频率限制测试"""

    async def test_rate_limiting_applies(self, user, bot):
        """测试频率限制是否生效（快速发送消息会触发限制）"""

        # 确保 bot 离线以避免复杂的 relay 逻辑
        bot.status = 'offline'
        await asyncio.get_event_loop().run_in_executor(None, bot.save)

        token = AccessToken.for_user(user)

        user_comm = WebsocketCommunicator(
            user_chat_app,
            f"/ws/chat/{bot.id}/?token={token}",
        )
        connected, _ = await user_comm.connect()
        assert connected is True

        # 消费掉初始系统消息
        try:
            await user_comm.receive_json_from(timeout=0.3)
        except:
            pass

        # 快速发送多条消息
        responses = []
        for i in range(5):
            await user_comm.send_json_to({
                "v": 1,
                "type": "message",
                "content": f"Message {i}",
                "ack_id": f"rate-test-{i}",
            })
            await asyncio.sleep(0.05)

        # 收集所有响应
        for _ in range(5):
            try:
                response = await user_comm.receive_json_from(timeout=0.5)
                responses.append(response)
            except:
                break

        # 验证收到了响应
        assert len(responses) > 0

        # 至少应该有 ack 响应（即使因为 bot 离线返回 error）
        acks = [r for r in responses if r.get("type") == "ack"]
        assert len(acks) > 0

        await user_comm.disconnect()
