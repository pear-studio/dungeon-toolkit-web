import pytest
from apps.characters.serializers import (
    CharacterListSerializer,
    CharacterDetailSerializer,
    CharacterCreateSerializer,
)
from apps.characters.models import Character


@pytest.mark.django_db
class TestCharacterListSerializer:
    def test_serialize_character(self, character):
        serializer = CharacterListSerializer(character)
        data = serializer.data
        assert data['name'] == character.name
        assert data['level'] == character.level
        assert 'id' in data

    def test_fields_included(self, character):
        serializer = CharacterListSerializer(character)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'gender', 'age', 'level',
            'ruleset_slug', 'race_slug', 'subrace_slug', 'class_slug', 'background_slug',
            'alignment',
            'is_public', 'created_at', 'updated_at',
        ]
        for field in expected_fields:
            assert field in data


@pytest.mark.django_db
class TestCharacterDetailSerializer:
    def test_serialize_with_ability_scores(self, character):
        serializer = CharacterDetailSerializer(character)
        data = serializer.data
        assert 'ability_scores' in data
        assert data['ability_scores']['str'] == character.strength
        assert data['ability_scores']['dex'] == character.dexterity

    def test_includes_all_detail_fields(self, character):
        serializer = CharacterDetailSerializer(character)
        data = serializer.data
        assert 'inventory' in data
        assert 'known_spells' in data
        assert 'share_token' in data


@pytest.mark.django_db
class TestCharacterCreateSerializer:
    def test_valid_create_data(self, user):
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
        from unittest.mock import MagicMock
        request = MagicMock()
        request.user = user
        serializer = CharacterCreateSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors

    def test_validate_name_empty_raises_error(self, user):
        data = {
            'name': '   ',
            'race_slug': 'human',
            'class_slug': 'fighter',
            'background_slug': 'soldier',
        }
        from unittest.mock import MagicMock
        request = MagicMock()
        request.user = user
        serializer = CharacterCreateSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_ability_scores_mapping(self, user):
        data = {
            'name': 'TestCharacter',
            'race_slug': 'human',
            'class_slug': 'fighter',
            'background_slug': 'soldier',
            'ability_scores': {
                'str': 15,
                'dex': 14,
                'con': 13,
                'int': 12,
                'wis': 10,
                'cha': 8,
            }
        }
        from unittest.mock import MagicMock
        request = MagicMock()
        request.user = user
        serializer = CharacterCreateSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        validated = serializer.validated_data
        assert validated['strength'] == 15
        assert validated['dexterity'] == 14
