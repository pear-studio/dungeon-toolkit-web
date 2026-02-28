import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User


@pytest.mark.django_db
class TestAuthViews:
    def test_register_success(self, api_client):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_register_duplicate_email(self, api_client, user):
        url = reverse('register')
        data = {
            'email': user.email,
            'username': 'anotheruser',
            'password': 'password123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success_with_email(self, api_client, user):
        url = reverse('login')
        data = {
            'identifier': user.email,
            'password': 'TestPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'user' in response.data

    def test_login_success_with_username(self, api_client, user):
        url = reverse('login')
        data = {
            'identifier': user.username,
            'password': 'TestPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_invalid_credentials(self, api_client, user):
        url = reverse('login')
        data = {
            'identifier': user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_requires_authentication(self, api_client):
        url = reverse('me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_user_info(self, authenticated_client, user):
        url = reverse('me')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username
