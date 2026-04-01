import secrets

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bots import consumers as bot_consumers
from apps.bots.models import Bot
from config.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_user_websocket_rejects_missing_or_invalid_jwt(user):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200001',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key=secrets.token_hex(32),
    )

    communicator = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/')
    connected, _ = await communicator.connect()
    assert connected is False

    communicator = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token=invalid')
    connected, _ = await communicator.connect()
    assert connected is False


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_bot_gateway_rejects_invalid_auth(user):
    await sync_to_async(Bot.objects.create)(
        bot_id='200002',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='valid-key',
    )

    communicator = WebsocketCommunicator(application, '/ws/bot/')
    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({'v': 1, 'type': 'auth', 'api_key': 'wrong-key'})
    await communicator.wait(timeout=1)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_relay_roundtrip_and_rate_limit(user):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200003',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='bot-key',
    )

    bot_comm = WebsocketCommunicator(application, '/ws/bot/')
    connected, _ = await bot_comm.connect()
    assert connected is True
    await bot_comm.send_json_to({'v': 1, 'type': 'auth', 'api_key': 'bot-key'})

    token = await sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()
    user_comm = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    connected, _ = await user_comm.connect()
    assert connected is True

    for idx in range(3):
        ack_id = f'ack-{idx}'
        await user_comm.send_json_to(
            {
                'v': 1,
                'type': 'message',
                'content': f'message-{idx}',
                'ack_id': ack_id,
            }
        )

        to_bot = await bot_comm.receive_json_from(timeout=1)
        assert to_bot['type'] == 'user_message'
        assert to_bot['ack_id'] == ack_id
        assert to_bot['v'] == 1

        ack = await user_comm.receive_json_from(timeout=1)
        assert ack['type'] == 'ack'
        assert ack['status'] == 'ok'
        assert ack['ack_id'] == ack_id

    await bot_comm.send_json_to(
        {
            'v': 1,
            'type': 'bot_message',
            'user_id': str(user.id),
            'content': 'hello-from-bot',
            'correlation_id': 'ack-2',
        }
    )
    inbound = await user_comm.receive_json_from(timeout=1)
    assert inbound['type'] == 'bot_message'
    assert inbound['content'] == 'hello-from-bot'
    assert inbound['correlation_id'] == 'ack-2'

    await user_comm.send_json_to(
        {
            'v': 1,
            'type': 'message',
            'content': 'message-over-limit',
            'ack_id': 'ack-over',
        }
    )
    over_ack = await user_comm.receive_json_from(timeout=1)
    assert over_ack['type'] == 'ack'
    assert over_ack['status'] == 'error'
    assert over_ack['ack_id'] == 'ack-over'
    assert await bot_comm.receive_nothing(timeout=0.2)

    await user_comm.disconnect()
    await bot_comm.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_second_tab_kicks_first_tab_for_same_user_and_bot(user):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200004',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='bot-key-2',
    )
    token = await sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()

    bot_comm = WebsocketCommunicator(application, '/ws/bot/')
    connected, _ = await bot_comm.connect()
    assert connected is True
    await bot_comm.send_json_to({'v': 1, 'type': 'auth', 'api_key': 'bot-key-2'})

    tab_1 = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    tab_2 = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    connected_1, _ = await tab_1.connect()
    connected_2, _ = await tab_2.connect()
    assert connected_1 is True
    assert connected_2 is True

    first_tab_notice = await tab_1.receive_json_from(timeout=1)
    assert first_tab_notice['type'] == 'system'
    assert first_tab_notice['code'] == 'FORCE_DISCONNECT'

    close_event = await tab_1.receive_output(timeout=1)
    assert close_event['type'] == 'websocket.close'
    assert close_event['code'] == 4001

    await tab_2.send_json_to(
        {
            'v': 1,
            'type': 'message',
            'content': 'new-tab-message',
            'ack_id': 'ack-new-tab',
        }
    )
    to_bot = await bot_comm.receive_json_from(timeout=1)
    assert to_bot['type'] == 'user_message'
    assert to_bot['ack_id'] == 'ack-new-tab'
    ack = await tab_2.receive_json_from(timeout=1)
    assert ack['type'] == 'ack'
    assert ack['status'] == 'ok'

    await bot_comm.send_json_to(
        {
            'v': 1,
            'type': 'bot_message',
            'user_id': str(user.id),
            'content': 'broadcast-test',
        }
    )
    msg_2 = await tab_2.receive_json_from(timeout=1)
    assert msg_2['content'] == 'broadcast-test'

    await tab_1.wait(timeout=1)
    await tab_2.disconnect()
    await bot_comm.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_offline_bot_sends_system_and_ack_error(user):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200005',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='bot-offline-key',
    )
    token = await sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()

    user_comm = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    connected, _ = await user_comm.connect()
    assert connected is True

    system_at_connect = await user_comm.receive_json_from(timeout=1)
    assert system_at_connect['type'] == 'system'

    await user_comm.send_json_to(
        {
            'v': 1,
            'type': 'message',
            'content': 'offline-message',
            'ack_id': 'offline-ack',
        }
    )
    ack = await user_comm.receive_json_from(timeout=1)
    system_after_send = await user_comm.receive_json_from(timeout=1)
    assert ack['type'] == 'ack'
    assert ack['status'] == 'error'
    assert system_after_send['type'] == 'system'

    await user_comm.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_rate_limit_allows_messages_after_window_reset(user, mocker):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200006',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='bot-key-3',
    )
    token = await sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()

    bot_comm = WebsocketCommunicator(application, '/ws/bot/')
    connected, _ = await bot_comm.connect()
    assert connected is True
    await bot_comm.send_json_to({'v': 1, 'type': 'auth', 'api_key': 'bot-key-3'})

    user_comm = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    connected, _ = await user_comm.connect()
    assert connected is True

    mocker.patch.object(
        bot_consumers.UserChatConsumer,
        '_current_time',
        side_effect=[100.0, 101.0, 102.0, 108.5],
    )

    for idx in range(4):
        ack_id = f'window-{idx}'
        await user_comm.send_json_to(
            {
                'v': 1,
                'type': 'message',
                'content': f'boundary-{idx}',
                'ack_id': ack_id,
            }
        )

        to_bot = await bot_comm.receive_json_from(timeout=1)
        assert to_bot['type'] == 'user_message'
        assert to_bot['ack_id'] == ack_id

        ack = await user_comm.receive_json_from(timeout=1)
        assert ack['type'] == 'ack'
        assert ack['status'] == 'ok'

    await user_comm.disconnect()
    await bot_comm.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_gateway_does_not_require_application_level_pong(user):
    bot = await sync_to_async(Bot.objects.create)(
        bot_id='200007',
        nickname='GatewayBot',
        master=user,
        master_qq='123456',
        api_key='bot-key-4',
    )
    token = await sync_to_async(lambda: str(RefreshToken.for_user(user).access_token))()

    bot_comm = WebsocketCommunicator(application, '/ws/bot/')
    connected, _ = await bot_comm.connect()
    assert connected is True
    await bot_comm.send_json_to({'v': 1, 'type': 'auth', 'api_key': 'bot-key-4'})

    user_comm = WebsocketCommunicator(application, f'/ws/chat/{bot.id}/?token={token}')
    connected, _ = await user_comm.connect()
    assert connected is True

    await user_comm.send_json_to(
        {
            'v': 1,
            'type': 'message',
            'content': 'no-app-pong-needed',
            'ack_id': 'ack-no-pong',
        }
    )

    to_bot = await bot_comm.receive_json_from(timeout=1)
    assert to_bot['type'] == 'user_message'
    assert to_bot['ack_id'] == 'ack-no-pong'

    ack = await user_comm.receive_json_from(timeout=1)
    assert ack['type'] == 'ack'
    assert ack['status'] == 'ok'

    # Sending legacy app-level pong should be ignored and not break relay.
    await bot_comm.send_json_to({'v': 1, 'type': 'pong'})
    await bot_comm.send_json_to(
        {
            'v': 1,
            'type': 'bot_message',
            'user_id': str(user.id),
            'content': 'still-alive',
        }
    )
    inbound = await user_comm.receive_json_from(timeout=1)
    assert inbound['type'] == 'bot_message'
    assert inbound['content'] == 'still-alive'

    await user_comm.disconnect()
    await bot_comm.disconnect()
