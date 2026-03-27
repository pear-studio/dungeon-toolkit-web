from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.bots.models import Bot
from .seed_test_data import PROFILE_CHOICES, get_fixture_bot_ids, get_fixture_usernames

User = get_user_model()


class Command(BaseCommand):
    help = '重置测试夹具数据（清理并重新 seed）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            choices=PROFILE_CHOICES,
            default='baseline',
            help='重置后 seed 使用的数据 profile',
        )
        parser.add_argument(
            '--no-strict',
            action='store_true',
            help='关闭严格校验，允许 seed 校验失败后继续返回',
        )

    def handle(self, *args, **options):
        profile = options['profile']
        strict = not options['no_strict']

        deleted_bots, _ = Bot.objects.filter(bot_id__in=get_fixture_bot_ids()).delete()
        deleted_users, _ = User.objects.filter(username__in=get_fixture_usernames()).delete()

        self.stdout.write(f'已清理机器人记录: {deleted_bots}')
        self.stdout.write(f'已清理用户记录: {deleted_users}')

        call_command('seed_test_data', profile=profile, strict=strict)
        mode_text = 'strict' if strict else 'non-strict'
        self.stdout.write(self.style.SUCCESS(f'测试数据重置完成 (profile={profile}, mode={mode_text})'))
