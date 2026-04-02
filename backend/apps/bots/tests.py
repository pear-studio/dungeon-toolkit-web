import pytest
import secrets
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from apps.bots.models import Bot
from apps.bots.chat_relay import BotConnectionRegistry


@pytest.mark.django_db
class TestWsStatusDiagnostic:
    """WebSocket 诊断端点测试"""

    @override_settings(DEBUG=True)
    def test_ws_status_admin_access(self, admin_client, admin_user):
        """admin 用户可访问诊断端点"""
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='TestBot',
            master=admin_user,
            master_qq='987654',
            api_key='test-api-key',
            status='offline'
        )
        url = f'/api/debug/ws-status/{bot.id}/'
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'registry' in response.data
        assert 'db' in response.data
        assert 'consistent' in response.data

    @override_settings(DEBUG=True)
    def test_ws_status_non_admin_forbidden(self, authenticated_client, user):
        """非 admin 用户 403"""
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='TestBot',
            master=user,
            master_qq='987654',
            api_key='test-api-key'
        )
        url = f'/api/debug/ws-status/{bot.id}/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @override_settings(DEBUG=True)
    def test_ws_status_unauthenticated(self, api_client):
        """未认证用户 401"""
        url = '/api/debug/ws-status/123e4567-e89b-12d3-a456-426614174000/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_ws_status_bot_not_found(self, admin_client):
        """不存在的 bot 返回 404"""
        import uuid
        url = f'/api/debug/ws-status/{uuid.uuid4()}/'
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @override_settings(DEBUG=True)
    def test_ws_status_consistent_state(self, admin_client, admin_user):
        """状态一致: registry offline, db offline"""
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='TestBot',
            master=admin_user,
            master_qq='987654',
            api_key='test-api-key',
            status='offline'
        )
        url = f'/api/debug/ws-status/{bot.id}/'
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['registry']['is_online'] is False
        assert response.data['db']['status'] == 'offline'
        assert response.data['consistent'] is True

    @override_settings(DEBUG=True)
    def test_ws_status_inconsistent_state(self, admin_client, admin_user):
        """状态不一致: registry online (模拟), db offline"""
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='TestBot',
            master=admin_user,
            master_qq='987654',
            api_key='test-inconsistent-key',
            status='offline'
        )
        # 模拟 registry 在线状态
        BotConnectionRegistry.bind('test-inconsistent-key', 'specific.channel.test')

        try:
            url = f'/api/debug/ws-status/{bot.id}/'
            response = admin_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data['registry']['is_online'] is True
            assert response.data['db']['status'] == 'offline'
            assert response.data['consistent'] is False
        finally:
            # 清理
            BotConnectionRegistry.unbind('test-inconsistent-key', 'specific.channel.test')

    @pytest.mark.django_db
    def test_ws_status_debug_false_route_not_found(self, admin_user):
        """DEBUG=False 时诊断端点路由不存在"""
        from django.test import override_settings
        from django.urls import resolve, Resolver404, clear_url_caches
        import uuid
        import importlib
        import config.urls

        with override_settings(DEBUG=False):
            clear_url_caches()
            importlib.reload(config.urls)
            url_path = f'/api/debug/ws-status/{uuid.uuid4()}/'
            with pytest.raises(Resolver404):
                resolve(url_path)


@pytest.mark.django_db
class TestBotRegistration:
    def test_register_new_bot(self, api_client):
        url = '/api/bots/register/'
        data = {
            'bot_id': '123456',
            'nickname': 'TestBot',
            'master_id': '987654',
            'version': 'v1.0.0',
            'description': 'A test bot'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'api_key' in response.data
        assert response.data['bot_id'] == '123456'
        assert response.data['nickname'] == 'TestBot'

    def test_register_duplicate_bot(self, api_client, user):
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='ExistingBot',
            master=user,
            master_qq='987654',
            api_key='test-api-key'
        )
        url = '/api/bots/register/'
        data = {
            'bot_id': '123456',
            'nickname': 'UpdatedBot',
            'master_id': '987654',
            'version': 'v2.0.0'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nickname'] == 'UpdatedBot'
        assert response.data['api_key'] != 'test-api-key'

    def test_register_missing_fields(self, api_client):
        url = '/api/bots/register/'
        data = {'bot_id': '123456'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBotHeartbeat:
    def test_heartbeat_with_valid_key(self, api_client, user):
        bot = Bot.objects.create(
            bot_id='123456',
            nickname='TestBot',
            master=user,
            master_qq='987654',
            api_key='valid-api-key',
            status='unknown'
        )
        url = '/api/bots/heartbeat/'
        response = api_client.post(
            url,
            {'status': 'online'},
            format='json',
            HTTP_X_API_KEY='valid-api-key'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'online'
        bot.refresh_from_db()
        assert bot.status == 'online'
        assert bot.last_seen is not None

    def test_heartbeat_with_invalid_key(self, api_client):
        url = '/api/bots/heartbeat/'
        response = api_client.post(
            url,
            {'status': 'online'},
            format='json',
            HTTP_X_API_KEY='invalid-key'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBotList:
    def test_list_public_bots(self, api_client, user):
        Bot.objects.create(
            bot_id='123456',
            nickname='PublicBot',
            master=user,
            master_qq='987654',
            is_public=True,
            api_key=secrets.token_hex(32)
        )
        Bot.objects.create(
            bot_id='654321',
            nickname='PrivateBot',
            master=user,
            master_qq='987654',
            is_public=False,
            api_key=secrets.token_hex(32)
        )
        url = '/api/bots/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['nickname'] == 'PublicBot'


@pytest.mark.django_db
class TestBotCRUD:
    def test_create_bot_authenticated(self, authenticated_client, user):
        url = '/api/bots/'
        data = {
            'bot_id': '111111',
            'nickname': 'NewBot',
            'master_qq': '111222',
            'is_public': True
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_own_bot(self, authenticated_client, user):
        bot = Bot.objects.create(
            bot_id='111111',
            nickname='MyBot',
            master=user,
            master_qq='111222',
            is_public=True,
            api_key=secrets.token_hex(32)
        )
        url = f'/api/bots/{bot.id}/update/'
        response = authenticated_client.patch(
            url,
            {'nickname': 'UpdatedBot'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        bot.refresh_from_db()
        assert bot.nickname == 'UpdatedBot'

    def test_cannot_update_other_bot(self, authenticated_client, user, other_user):
        bot = Bot.objects.create(
            bot_id='111111',
            nickname='OtherBot',
            master=other_user,
            master_qq='111222',
            is_public=True,
            api_key=secrets.token_hex(32)
        )
        url = f'/api/bots/{bot.id}/update/'
        response = authenticated_client.patch(
            url,
            {'nickname': 'Hacked'},
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_own_bot(self, authenticated_client, user):
        bot = Bot.objects.create(
            bot_id='111111',
            nickname='MyBot',
            master=user,
            master_qq='111222',
            is_public=True,
            api_key=secrets.token_hex(32)
        )
        url = f'/api/bots/{bot.id}/delete/'
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Bot.objects.filter(id=bot.id).exists()

    def test_cannot_delete_other_bot(self, authenticated_client, user, other_user):
        bot = Bot.objects.create(
            bot_id='111111',
            nickname='OtherBot',
            master=other_user,
            master_qq='111222',
            is_public=True,
            api_key=secrets.token_hex(32)
        )
        url = f'/api/bots/{bot.id}/delete/'
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
