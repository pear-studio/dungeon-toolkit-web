"""
角色模型 - 存储用户创建的 D&D 角色数据
"""
import uuid
from django.db import models
from django.conf import settings


class Character(models.Model):
    """D&D 角色"""

    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
        ('other', '其他'),
        ('unknown', '未知'),
    ]

    ABILITY_METHOD_CHOICES = [
        ('standard_array', '标准数组'),
        ('point_buy', '点数购买'),
        ('manual', '手动输入'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='characters',
    )

    # ── 基础信息 ──────────────────────────────────────────
    name = models.CharField(max_length=100, help_text='角色名')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    appearance = models.TextField(blank=True, help_text='外貌描述')
    backstory = models.TextField(blank=True, help_text='背景故事')

    # ── 规则集与来源数据关联（存 slug，不做外键，避免删除游戏数据影响角色）──
    ruleset_slug = models.CharField(max_length=50, help_text='规则集 slug')
    race_slug = models.CharField(max_length=50, help_text='种族 slug')
    subrace_slug = models.CharField(max_length=50, blank=True, help_text='亚种族 slug')
    class_slug = models.CharField(max_length=50, help_text='职业 slug')
    background_slug = models.CharField(max_length=50, help_text='背景 slug')

    # ── 等级与经验 ──────────────────────────────────────────
    level = models.PositiveSmallIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)

    # ── 六维属性（基础值，不含种族加值）──────────────────────────────────────────
    ability_method = models.CharField(
        max_length=20, choices=ABILITY_METHOD_CHOICES, default='standard_array'
    )
    strength = models.PositiveSmallIntegerField(default=10)
    dexterity = models.PositiveSmallIntegerField(default=10)
    constitution = models.PositiveSmallIntegerField(default=10)
    intelligence = models.PositiveSmallIntegerField(default=10)
    wisdom = models.PositiveSmallIntegerField(default=10)
    charisma = models.PositiveSmallIntegerField(default=10)

    # ── 技能熟练 ──────────────────────────────────────────
    # ["athletics", "arcana", ...]
    skill_proficiencies = models.JSONField(default=list)

    # ── 阵营 ──────────────────────────────────────────
    alignment = models.CharField(max_length=30, blank=True, help_text='阵营 slug，如 lawful-good')

    # ── 性格扮演 ──────────────────────────────────────────
    personality_trait = models.TextField(blank=True)
    ideal = models.TextField(blank=True)
    bond = models.TextField(blank=True)
    flaw = models.TextField(blank=True)

    # ── 法术 ──────────────────────────────────────────
    # [{"slug": "fire-bolt", "name": "火焰冲击"}, ...]
    known_spells = models.JSONField(default=list, help_text='已知法术列表')
    prepared_spells = models.JSONField(default=list, help_text='已准备法术列表')

    # ── 装备/物品 ──────────────────────────────────────────
    # [{"name": "链甲", "quantity": 1, "description": "..."}]
    inventory = models.JSONField(default=list, help_text='物品栏')

    # ── 货币 ──────────────────────────────────────────
    copper = models.PositiveIntegerField(default=0)
    silver = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)
    platinum = models.PositiveIntegerField(default=0)

    # ── 分享 ──────────────────────────────────────────
    is_public = models.BooleanField(default=False, help_text='是否公开分享')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, help_text='分享链接Token')

    # ── 时间戳 ──────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} (Lv.{self.level} {self.class_slug})'
