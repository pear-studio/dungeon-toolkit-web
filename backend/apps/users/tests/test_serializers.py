import pytest
from apps.users.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from apps.users.models import User


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_valid_registration(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.email == 'newuser@example.com'
        assert user.username == 'newuser'
        assert user.check_password('password123')

    def test_registration_password_too_short(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'short'
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_registration_missing_fields(self):
        data = {'email': 'test@example.com'}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestLoginSerializer:
    def test_valid_login_with_email(self, user):
        data = {
            'identifier': 'test@example.com',
            'password': 'TestPass123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['user'] == user

    def test_valid_login_with_username(self, user):
        data = {
            'identifier': 'testuser',
            'password': 'TestPass123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['user'] == user

    def test_invalid_password(self, user):
        data = {
            'identifier': 'testuser',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_invalid_identifier(self):
        data = {
            'identifier': 'nonexistent',
            'password': 'password123'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestUserSerializer:
    def test_serialize_user(self, user):
        serializer = UserSerializer(user)
        assert serializer.data['email'] == user.email
        assert serializer.data['username'] == user.username
        assert 'id' in serializer.data
        assert 'date_joined' in serializer.data
