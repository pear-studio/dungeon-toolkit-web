from rest_framework import serializers
from .models import Ruleset, Race, Subrace, CharClass, Subclass, Background, Spell


class RulesetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruleset
        fields = ['id', 'slug', 'name', 'description', 'is_active']


class SubraceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subrace
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'ability_bonuses', 'traits']


class RaceListSerializer(serializers.ModelSerializer):
    """种族列表（精简版，用于向导卡片展示）"""
    class Meta:
        model = Race
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'speed', 'size',
                  'ability_bonuses', 'has_subraces']


class RaceDetailSerializer(serializers.ModelSerializer):
    """种族详情（含亚种族）"""
    subraces = SubraceSerializer(many=True, read_only=True)

    class Meta:
        model = Race
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'speed', 'size',
                  'ability_bonuses', 'traits', 'languages', 'has_subraces', 'subraces']


class SubclassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subclass
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'features']


class CharClassListSerializer(serializers.ModelSerializer):
    """职业列表（精简版，用于向导卡片展示）"""
    class Meta:
        model = CharClass
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'hit_die',
                  'primary_ability', 'is_spellcaster', 'roles']


class CharClassDetailSerializer(serializers.ModelSerializer):
    """职业详情（含子职业）"""
    subclasses = SubclassSerializer(many=True, read_only=True)

    class Meta:
        model = CharClass
        fields = ['id', 'slug', 'name', 'name_en', 'description', 'hit_die',
                  'primary_ability', 'saving_throw_proficiencies', 'armor_proficiencies',
                  'weapon_proficiencies', 'skill_choices_count', 'skill_choices',
                  'is_spellcaster', 'spellcasting_ability', 'level_features',
                  'starting_equipment', 'roles', 'subclasses']


class BackgroundListSerializer(serializers.ModelSerializer):
    """背景列表（精简版）"""
    class Meta:
        model = Background
        fields = ['id', 'slug', 'name', 'name_en', 'description',
                  'skill_proficiencies', 'feature_name']


class BackgroundDetailSerializer(serializers.ModelSerializer):
    """背景详情（含性格特质预设）"""
    class Meta:
        model = Background
        fields = ['id', 'slug', 'name', 'name_en', 'description',
                  'skill_proficiencies', 'tool_proficiencies', 'languages_count',
                  'feature_name', 'feature_description', 'starting_equipment',
                  'starting_gold', 'personality_traits', 'ideals', 'bonds', 'flaws']


class SpellListSerializer(serializers.ModelSerializer):
    """法术列表（精简版）"""
    school_display = serializers.CharField(source='get_school_display', read_only=True)

    class Meta:
        model = Spell
        fields = ['id', 'slug', 'name', 'name_en', 'level', 'school', 'school_display',
                  'casting_time', 'range', 'duration', 'concentration', 'ritual', 'classes']


class SpellDetailSerializer(serializers.ModelSerializer):
    """法术详情"""
    school_display = serializers.CharField(source='get_school_display', read_only=True)

    class Meta:
        model = Spell
        fields = ['id', 'slug', 'name', 'name_en', 'level', 'school', 'school_display',
                  'casting_time', 'range', 'components', 'material', 'duration',
                  'concentration', 'ritual', 'description', 'higher_levels', 'classes']
