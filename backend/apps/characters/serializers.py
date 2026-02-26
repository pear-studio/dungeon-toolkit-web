from rest_framework import serializers
from .models import Character


class CharacterListSerializer(serializers.ModelSerializer):
    """角色列表（精简版，用于卡片展示）"""

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'gender', 'age', 'level',
            'ruleset_slug', 'race_slug', 'subrace_slug', 'class_slug', 'background_slug',
            'alignment',
            'is_public', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CharacterDetailSerializer(serializers.ModelSerializer):
    """角色详情（完整字段）"""

    # 前端友好的 ability_scores 字典（只读，用于展示）
    ability_scores = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'gender', 'age', 'appearance', 'backstory',
            'ruleset_slug', 'race_slug', 'subrace_slug', 'class_slug', 'background_slug',
            'level', 'experience_points',
            'ability_method',
            'strength', 'dexterity', 'constitution',
            'intelligence', 'wisdom', 'charisma',
            'ability_scores',
            'alignment',
            'skill_proficiencies',
            'personality_trait', 'ideal', 'bond', 'flaw',
            'known_spells', 'prepared_spells',
            'inventory',
            'copper', 'silver', 'gold', 'platinum',
            'is_public', 'share_token',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'share_token', 'created_at', 'updated_at']

    def get_ability_scores(self, obj):
        return {
            'str': obj.strength,
            'dex': obj.dexterity,
            'con': obj.constitution,
            'int': obj.intelligence,
            'wis': obj.wisdom,
            'cha': obj.charisma,
        }


class CharacterCreateSerializer(serializers.ModelSerializer):
    """创建角色（向导提交用）"""

    # 接受前端传来的 {str, dex, con, int, wis, cha} 字典，write_only
    ability_scores = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=30),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'gender', 'age', 'appearance', 'backstory',
            'ruleset_slug', 'race_slug', 'subrace_slug', 'class_slug', 'background_slug',
            'level', 'ability_method',
            'strength', 'dexterity', 'constitution',
            'intelligence', 'wisdom', 'charisma',
            'ability_scores',
            'alignment',
            'skill_proficiencies',
            'personality_trait', 'ideal', 'bond', 'flaw',
            'known_spells', 'inventory',
            'copper', 'silver', 'gold', 'platinum',
        ]
        read_only_fields = ['id']
        # 单独字段设为可选，由 ability_scores 字典覆盖
        extra_kwargs = {
            'strength':     {'required': False},
            'dexterity':    {'required': False},
            'constitution': {'required': False},
            'intelligence': {'required': False},
            'wisdom':       {'required': False},
            'charisma':     {'required': False},
            'ruleset_slug': {'required': False, 'default': 'phb2014'},
            'subrace_slug': {'required': False, 'default': ''},
            'level':        {'required': False},
        }

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('角色名不能为空')
        return value.strip()

    def validate(self, attrs):
        # 将 ability_scores 字典映射到具体字段
        scores = attrs.pop('ability_scores', None)
        if scores:
            key_map = {
                'str': 'strength', 'dex': 'dexterity', 'con': 'constitution',
                'int': 'intelligence', 'wis': 'wisdom', 'cha': 'charisma',
            }
            for short, full in key_map.items():
                if short in scores:
                    attrs[full] = scores[short]
        return attrs

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        # 若前端未传 ruleset_slug，默认 phb2014
        validated_data.setdefault('ruleset_slug', 'phb2014')
        return super().create(validated_data)


class CharacterPublicSerializer(serializers.ModelSerializer):
    """公开分享页（只读，不含敏感信息）"""

    ability_scores = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'gender', 'age', 'appearance', 'backstory',
            'ruleset_slug', 'race_slug', 'subrace_slug', 'class_slug', 'background_slug',
            'level',
            'strength', 'dexterity', 'constitution',
            'intelligence', 'wisdom', 'charisma',
            'ability_scores',
            'alignment',
            'skill_proficiencies',
            'personality_trait', 'ideal', 'bond', 'flaw',
            'known_spells', 'inventory',
            'created_at',
        ]

    def get_ability_scores(self, obj):
        return {
            'str': obj.strength,
            'dex': obj.dexterity,
            'con': obj.constitution,
            'int': obj.intelligence,
            'wis': obj.wisdom,
            'cha': obj.charisma,
        }