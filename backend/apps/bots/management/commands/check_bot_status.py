from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.bots.models import Bot


class Command(BaseCommand):
    help = '检查并更新机器人在线状态'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout-minutes',
            type=int,
            default=5,
            help='超过此分钟数未收到心跳则视为离线 (默认: 5)'
        )

    def handle(self, *args, **options):
        timeout_minutes = options['timeout_minutes']
        threshold = timezone.now() - timedelta(minutes=timeout_minutes)

        offline_bots = Bot.objects.filter(
            status='online',
            last_seen__lt=threshold
        ).update(status='offline')

        unknown_bots = Bot.objects.filter(
            status='unknown',
            last_seen__isnull=True
        )

        for bot in unknown_bots:
            if bot.last_seen is None:
                bot.status = 'unknown'

        self.stdout.write(
            self.style.SUCCESS(f'已更新 {offline_bots} 个机器人状态为离线')
        )
