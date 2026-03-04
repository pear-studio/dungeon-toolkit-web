import uuid
from django.db import models
from django.conf import settings


class Bot(models.Model):
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('unknown', '未知'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot_id = models.CharField(max_length=20, unique=True, verbose_name='机器人QQ号')
    nickname = models.CharField(max_length=100, verbose_name='昵称')
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bots',
        verbose_name='主人'
    )
    master_qq = models.CharField(max_length=20, verbose_name='主人QQ号')
    version = models.CharField(max_length=50, blank=True, default='', verbose_name='版本')
    api_key = models.CharField(max_length=64, unique=True, verbose_name='API Key')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    is_public = models.BooleanField(default=True, verbose_name='公开显示')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='unknown',
        verbose_name='在线状态'
    )
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='最后在线')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '机器人'
        verbose_name_plural = '机器人'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nickname} ({self.bot_id})'
