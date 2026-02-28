import pytest
from django.contrib.auth import get_user_model
from apps.users.models import User

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_empty_email(self):
        user = User.objects.create_user(
            username='testuser',
            email='',
            password='testpass123'
        )
        assert user.email == ''

    def test_create_user_with_duplicate_email_raises_error(self):
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='testpass123'
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert user.is_staff
        assert user.is_superuser

    def test_user_str(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'

    def test_user_default_avatar(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.avatar == ''
