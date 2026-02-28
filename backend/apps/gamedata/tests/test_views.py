import pytest
from django.urls import reverse
from rest_framework import status
from apps.gamedata.models import Ruleset, Race, CharClass, Background


@pytest.mark.django_db
class TestRulesetViewSet:
    def test_list_rulesets(self, authenticated_client):
        Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        url = reverse('ruleset-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_list_rulesets_unauthenticated(self, api_client):
        url = reverse('ruleset-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRaceViewSet:
    def test_list_races(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        Race.objects.create(
            ruleset=ruleset,
            slug='human',
            name='人类',
            has_subraces=False,
        )
        url = reverse('race-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_races_by_ruleset(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='test_ruleset', name='Test', is_active=True)
        Race.objects.create(ruleset=ruleset, slug='elf', name='精灵')
        url = f"{reverse('race-list')}?ruleset__slug=test_ruleset"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_race_detail(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        race = Race.objects.create(
            ruleset=ruleset,
            slug='elf',
            name='精灵',
            has_subraces=True,
        )
        url = reverse('race-detail', kwargs={'pk': race.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['slug'] == 'elf'


@pytest.mark.django_db
class TestCharClassViewSet:
    def test_list_classes(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        CharClass.objects.create(
            ruleset=ruleset,
            slug='wizard',
            name='法师',
            hit_die=6,
            primary_ability='智力',
            is_spellcaster=True,
        )
        url = reverse('charclass-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_classes_by_ruleset(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='test_ruleset', name='Test', is_active=True)
        CharClass.objects.create(ruleset=ruleset, slug='fighter', name='战士', hit_die=10)
        url = f"{reverse('charclass-list')}?ruleset__slug=test_ruleset"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_spellcasters(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='test', name='Test', is_active=True)
        CharClass.objects.create(ruleset=ruleset, slug='wizard', name='法师', hit_die=6, primary_ability='智力', is_spellcaster=True)
        CharClass.objects.create(ruleset=ruleset, slug='fighter', name='战士', hit_die=10, primary_ability='力量', is_spellcaster=False)
        url = f"{reverse('charclass-list')}?is_spellcaster=true"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestBackgroundViewSet:
    def test_list_backgrounds(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        Background.objects.create(
            ruleset=ruleset,
            slug='sage',
            name='学者',
            feature_name='研究者',
            feature_description='通过研究获取信息',
        )
        url = reverse('background-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_background_detail(self, authenticated_client):
        ruleset = Ruleset.objects.create(slug='dnd5e_2014', name='D&D 5e 2014', is_active=True)
        bg = Background.objects.create(
            ruleset=ruleset,
            slug='soldier',
            name='士兵',
            feature_name='军事训练',
            feature_description='熟悉战争',
        )
        url = reverse('background-detail', kwargs={'pk': bg.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['slug'] == 'soldier'
