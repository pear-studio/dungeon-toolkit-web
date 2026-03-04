import pytest
from apps.characters.models import Character


@pytest.mark.django_db
class TestCharacterModel:
    def test_create_character(self, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        assert character.name == 'TestCharacter'
        assert character.owner == user
        assert character.level == 1
        assert character.is_public is False

    def test_character_default_ability_scores(self, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        assert character.strength == 10
        assert character.dexterity == 10
        assert character.constitution == 10
        assert character.intelligence == 10
        assert character.wisdom == 10
        assert character.charisma == 10

    def test_character_str(self, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='wizard',
            background_slug='sage',
            ruleset_slug='dnd5e_2014',
            level=5,
        )
        assert str(character) == 'TestCharacter (Lv.5 wizard)'

    def test_character_gender_choices(self, user):
        character = Character.objects.create(
            owner=user,
            name='TestCharacter',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            gender='male',
        )
        assert character.gender == 'male'

        character.gender = 'female'
        character.save()
        assert character.gender == 'female'

    def test_character_ordering(self, user):
        char1 = Character.objects.create(
            owner=user,
            name='Char1',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        char2 = Character.objects.create(
            owner=user,
            name='Char2',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
        )
        characters = list(Character.objects.all())
        assert characters[0] == char2
        assert characters[1] == char1

    def test_character_share_token_unique(self, user):
        char1 = Character.objects.create(
            owner=user,
            name='Char1',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            is_public=True,
        )
        char2 = Character.objects.create(
            owner=user,
            name='Char2',
            race_slug='human',
            class_slug='fighter',
            background_slug='soldier',
            ruleset_slug='dnd5e_2014',
            is_public=True,
        )
        assert char1.share_token != char2.share_token
