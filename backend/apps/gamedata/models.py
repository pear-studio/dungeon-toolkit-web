"""
游戏数据模型 - 存储 D&D 5e 规则数据（种族/职业/背景/法术等）
这些数据为只读参考数据，通过导入脚本填充，不由用户修改。
"""
from django.db import models


class Ruleset(models.Model):
    """规则集（如 D&D 5e 2014版、2024版）"""
    slug = models.SlugField(unique=True, help_text='唯一标识符，如 dnd5e_2014')
    name = models.CharField(max_length=100, help_text='显示名称')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Race(models.Model):
    """种族"""
    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE, related_name='races')
    slug = models.SlugField(help_text='唯一标识符，如 elf')
    name = models.CharField(max_length=100, help_text='中文名')
    name_en = models.CharField(max_length=100, blank=True, help_text='英文名')
    description = models.TextField(blank=True, help_text='种族简介')
    speed = models.PositiveSmallIntegerField(default=30, help_text='移动速度（尺）')
    size = models.CharField(max_length=20, default='中型', help_text='体型')
    # 属性加值，使用 JSONField 存储 {"str": 0, "dex": 2, ...}
    ability_bonuses = models.JSONField(default=dict, help_text='属性加值，如 {"dex": 2}')
    # 种族特性列表 [{"name": "黑暗视觉", "description": "..."}]
    traits = models.JSONField(default=list, help_text='种族特性列表')
    languages = models.JSONField(default=list, help_text='掌握语言列表')
    has_subraces = models.BooleanField(default=False, help_text='是否有亚种族')

    class Meta:
        unique_together = ('ruleset', 'slug')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.ruleset.slug})'


class Subrace(models.Model):
    """亚种族"""
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='subraces')
    slug = models.SlugField()
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    ability_bonuses = models.JSONField(default=dict, help_text='额外属性加值')
    traits = models.JSONField(default=list, help_text='亚种族特性列表')

    class Meta:
        unique_together = ('race', 'slug')
        ordering = ['name']

    def __str__(self):
        return f'{self.race.name} - {self.name}'


class CharClass(models.Model):
    """职业"""
    ROLE_CHOICES = [
        ('damage', '输出'),
        ('control', '控场'),
        ('support', '辅助'),
        ('tank', '坦克'),
    ]

    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE, related_name='classes')
    slug = models.SlugField(help_text='唯一标识符，如 wizard')
    name = models.CharField(max_length=100, help_text='中文名')
    name_en = models.CharField(max_length=100, blank=True, help_text='英文名')
    description = models.TextField(blank=True)
    hit_die = models.PositiveSmallIntegerField(help_text='命中骰面数，如 6/8/10/12')
    primary_ability = models.CharField(max_length=50, help_text='主要属性，如 智力')
    saving_throw_proficiencies = models.JSONField(default=list, help_text='豁免熟练项，如 ["int", "wis"]')
    armor_proficiencies = models.JSONField(default=list, help_text='护甲熟练项')
    weapon_proficiencies = models.JSONField(default=list, help_text='武器熟练项')
    skill_choices_count = models.PositiveSmallIntegerField(default=2, help_text='可选技能数量')
    skill_choices = models.JSONField(default=list, help_text='可选技能列表')
    is_spellcaster = models.BooleanField(default=False, help_text='是否有施法能力')
    spellcasting_ability = models.CharField(max_length=10, blank=True, help_text='施法属性，如 int')
    # 各等级特性：{"1": [{"name": "...", "description": "..."}], "2": [...]}
    level_features = models.JSONField(default=dict, help_text='各等级获得的特性')
    # 1级初始装备选项：[{"option": "a", "items": ["链甲"]}, {"option": "b", "items": ["皮甲","两把匕首"]}]
    starting_equipment = models.JSONField(default=list, help_text='初始装备选项')
    roles = models.JSONField(default=list, help_text='职业定位标签列表')

    class Meta:
        unique_together = ('ruleset', 'slug')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.ruleset.slug})'


class Subclass(models.Model):
    """子职业"""
    char_class = models.ForeignKey(CharClass, on_delete=models.CASCADE, related_name='subclasses')
    slug = models.SlugField()
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=dict, help_text='各等级获得的子职业特性')

    class Meta:
        unique_together = ('char_class', 'slug')
        ordering = ['name']

    def __str__(self):
        return f'{self.char_class.name} - {self.name}'


class Background(models.Model):
    """背景"""
    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE, related_name='backgrounds')
    slug = models.SlugField()
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    skill_proficiencies = models.JSONField(default=list, help_text='技能熟练项，如 ["insight", "religion"]')
    tool_proficiencies = models.JSONField(default=list, help_text='工具熟练项')
    languages_count = models.PositiveSmallIntegerField(default=0, help_text='额外语言数量')
    feature_name = models.CharField(max_length=100, help_text='背景特性名称')
    feature_description = models.TextField(help_text='背景特性描述')
    starting_equipment = models.JSONField(default=list, help_text='初始装备列表')
    starting_gold = models.PositiveSmallIntegerField(default=0, help_text='初始金币（gp）')
    # 性格特质预设（各4条）
    personality_traits = models.JSONField(default=list, help_text='性格特质预设列表（8条）')
    ideals = models.JSONField(default=list, help_text='理念预设列表（6条）')
    bonds = models.JSONField(default=list, help_text='牵绊预设列表（6条）')
    flaws = models.JSONField(default=list, help_text='缺点预设列表（6条）')

    class Meta:
        unique_together = ('ruleset', 'slug')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.ruleset.slug})'


class Spell(models.Model):
    """法术"""
    SCHOOL_CHOICES = [
        ('abjuration', '防护'),
        ('conjuration', '咒法'),
        ('divination', '预言'),
        ('enchantment', '惑控'),
        ('evocation', '塑能'),
        ('illusion', '幻术'),
        ('necromancy', '死灵'),
        ('transmutation', '变化'),
    ]

    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE, related_name='spells')
    slug = models.SlugField()
    name = models.CharField(max_length=100, help_text='中文名')
    name_en = models.CharField(max_length=100, blank=True)
    level = models.PositiveSmallIntegerField(help_text='法术环级，0=戏法')
    school = models.CharField(max_length=20, choices=SCHOOL_CHOICES)
    casting_time = models.CharField(max_length=50, help_text='施法时间，如 1个动作')
    range = models.CharField(max_length=50, help_text='射程')
    components = models.JSONField(default=list, help_text='法术成分，如 ["V", "S", "M"]')
    material = models.CharField(max_length=200, blank=True, help_text='材料成分详情')
    duration = models.CharField(max_length=50, help_text='持续时间')
    concentration = models.BooleanField(default=False, help_text='是否需要专注')
    ritual = models.BooleanField(default=False, help_text='是否可以仪式施法')
    description = models.TextField(help_text='法术描述')
    higher_levels = models.TextField(blank=True, help_text='高环施放效果')
    # 可使用该法术的职业列表
    classes = models.JSONField(default=list, help_text='可使用的职业 slug 列表，如 ["wizard", "sorcerer"]')

    class Meta:
        unique_together = ('ruleset', 'slug')
        ordering = ['level', 'name']

    def __str__(self):
        return f'[{self.level}环] {self.name}'
