import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.bots.models import Bot

User = get_user_model()


@pytest.mark.django_db
def test_seed_test_data_is_idempotent():
    call_command('seed_test_data', profile='baseline', strict=True)
    call_command('seed_test_data', profile='baseline', strict=True)

    assert User.objects.filter(username='fixture_normal').exists()
    assert User.objects.filter(username='fixture_expired').exists()
    assert User.objects.filter(username='fixture_refresh_fail').exists()

    fixture_bots = Bot.objects.filter(bot_id__in=['880001', '880002', '880003', '880004', '880005'])
    assert fixture_bots.count() == 5
    assert fixture_bots.filter(is_public=True).exists()
    assert fixture_bots.filter(status='online').exists()
    assert fixture_bots.filter(status='offline').exists()


@pytest.mark.django_db
def test_reset_test_data_restores_fixture_state():
    call_command('seed_test_data', profile='baseline', strict=True)
    Bot.objects.filter(bot_id='880001').update(is_public=False)
    Bot.objects.filter(bot_id='880003').delete()

    call_command('reset_test_data', profile='baseline')

    fixture_bots = Bot.objects.filter(bot_id__in=['880001', '880002', '880003', '880004', '880005'])
    assert fixture_bots.count() == 5
    assert fixture_bots.get(bot_id='880001').is_public is True
    assert fixture_bots.filter(is_public=True).exists()


@pytest.mark.django_db
def test_verify_test_data_raises_when_fixture_missing():
    call_command('seed_test_data', profile='baseline', strict=True)
    User.objects.filter(username='fixture_expired').delete()

    with pytest.raises(CommandError):
        call_command('verify_test_data', profile='baseline')


@pytest.mark.django_db
def test_verify_test_data_passes_for_baseline_profile():
    call_command('seed_test_data', profile='baseline', strict=True)
    call_command('verify_test_data', profile='baseline')


@pytest.mark.django_db
def test_empty_robot_plaza_profile_seed_and_verify():
    call_command('reset_test_data', profile='empty-robot-plaza')

    fixture_bots = Bot.objects.filter(bot_id__in=['880001', '880002', '880003', '880004', '880005'])
    assert fixture_bots.count() == 5
    assert fixture_bots.filter(is_public=True).count() == 0

    call_command('verify_test_data', profile='empty-robot-plaza')
