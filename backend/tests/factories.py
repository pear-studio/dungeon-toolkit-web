import factory
from factory.django import DjangoModelFactory
from apps.users.models import User
from apps.characters.models import Character
from apps.gamedata.models import Ruleset, Race, CharClass, Background


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    avatar = ''


class RulesetFactory(DjangoModelFactory):
    class Meta:
        model = Ruleset

    slug = factory.Sequence(lambda n: f'ruleset_{n}')
    name = factory.Sequence(lambda n: f'规则集 {n}')
    is_active = True


class RaceFactory(DjangoModelFactory):
    class Meta:
        model = Race

    ruleset = factory.SubFactory(RulesetFactory)
    slug = factory.Sequence(lambda n: f'race_{n}')
    name = factory.Sequence(lambda n: f'种族{n}')
    speed = 30
    size = '中型'
    ability_bonuses = {}
    traits = []
    languages = []
    has_subraces = False


class CharClassFactory(DjangoModelFactory):
    class Meta:
        model = CharClass

    ruleset = factory.SubFactory(RulesetFactory)
    slug = factory.Sequence(lambda n: f'class_{n}')
    name = factory.Sequence(lambda n: f'职业{n}')
    hit_die = 8
    primary_ability = '力量'
    saving_throw_proficiencies = []
    armor_proficiencies = []
    weapon_proficiencies = []
    skill_choices_count = 2
    skill_choices = []
    is_spellcaster = False
    level_features = {}
    starting_equipment = []


class BackgroundFactory(DjangoModelFactory):
    class Meta:
        model = Background

    ruleset = factory.SubFactory(RulesetFactory)
    slug = factory.Sequence(lambda n: f'background_{n}')
    name = factory.Sequence(lambda n: f'背景{n}')
    feature_name = '特性'
    feature_description = '特性描述'
    starting_equipment = []
    starting_gold = 0


class CharacterFactory(DjangoModelFactory):
    class Meta:
        model = Character

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'角色_{n}')
    gender = 'unknown'
    age = 25
    appearance = ''
    backstory = ''
    ruleset_slug = 'dnd5e_2014'
    race_slug = 'human'
    subrace_slug = ''
    class_slug = 'fighter'
    background_slug = 'soldier'
    level = 1
    experience_points = 0
    ability_method = 'standard_array'
    strength = 10
    dexterity = 10
    constitution = 10
    intelligence = 10
    wisdom = 10
    charisma = 10
    skill_proficiencies = []
    alignment = ''
    personality_trait = ''
    ideal = ''
    bond = ''
    flaw = ''
    known_spells = []
    prepared_spells = []
    inventory = []
    copper = 0
    silver = 0
    gold = 0
    platinum = 0
    is_public = False
