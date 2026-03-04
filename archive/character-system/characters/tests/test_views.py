import pytest
from django.urls import reverse
from rest_framework import status
from apps.characters.models import Character


@pytest.mark.django_db
class TestCharacterViewSet:
    def test_list_characters(self, authenticated_client, user):
        Character.objects.create(
            owner=user,
            name='Character1',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        url = reverse('character-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_character(self, authenticated_client, user):
        url = reverse('character-list')
        data = {
            'name': 'NewCharacter',
            'gender': 'male',
            'age': 25,
            'race_slug': 'elf',
            'class_slug': 'wizard',
            'background_slug': 'sage',
            'ability_scores': {
                'str': 8,
                'dex': 14,
                'con': 12,
                'int': 16,
                'wis': 10,
                'cha': 10,
            }
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'NewCharacter'
        assert Character.objects.filter(owner=user, name='NewCharacter').exists()

    def test_retrieve_character(self, authenticated_client, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        url = reverse('character-detail', kwargs={'pk': character.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'TestCharacter'

    def test_update_character(self, authenticated_client, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            level=1,
        )
        url = reverse('character-detail', kwargs={'pk': character.pk})
        response = authenticated_client.patch(url, {'level': 5}, format='json')
        assert response.status_code == status.HTTP_200_OK
        character.refresh_from_db()
        assert character.level == 5

    def test_delete_character(self, authenticated_client, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        url = reverse('character-detail', kwargs={'pk': character.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Character.objects.filter(pk=character.pk).exists()

    def test_cannot_access_other_user_character(self, authenticated_client, user):
        from apps.users.models import User
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password123'
        )
        character = Character.objects.create(
            owner=other_user,
            name='OtherCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        url = reverse('character-detail', kwargs={'pk': character.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_toggle_share(self, authenticated_client, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            is_public=False,
        )
        url = reverse('character-detail', kwargs={'pk': character.pk}) + 'share/'
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        character.refresh_from_db()
        assert character.is_public is True

    def test_list_requires_auth(self, api_client):
        url = reverse('character-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCharacterPublicView:
    def test_public_access_with_token(self, api_client, user):
        character = Character.objects.create(
            owner=user,
            name='PublicCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            is_public=True,
        )
        url = f"/api/characters/public/{character.share_token}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'PublicCharacter'

    def test_private_character_not_accessible(self, api_client, user):
        character = Character.objects.create(
            owner=user,
            name='PrivateCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            is_public=False,
        )
        url = f"/api/characters/public/{character.share_token}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
