import pytest
import secrets
from django.urls import reverse
from rest_framework import status
from apps.bots.models import Bot


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
