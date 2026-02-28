import pytest
from django.contrib.auth import get_user_model
from apps.characters.models import Character

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123'
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123'
    )


@pytest.fixture
def character(db, user):
    return Character.objects.create(
        owner=user,
        name='TestCharacter',
        race_slug='human',
        class_slug='fighter',
        background_slug='soldier',
        ruleset_slug='dnd5e_2014',
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
