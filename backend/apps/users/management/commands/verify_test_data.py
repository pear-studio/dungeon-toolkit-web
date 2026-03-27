from django.core.management.base import BaseCommand, CommandError

from .seed_test_data import PROFILE_CHOICES, build_validation_checks

class Command(BaseCommand):
    help = '验证测试夹具数据是否完整'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            choices=PROFILE_CHOICES,
            default='baseline',
            help='按指定 profile 执行校验',
        )

    def handle(self, *args, **options):
        profile = options['profile']

        checks = build_validation_checks(profile=profile)

        failed = []
        for name, ok in checks:
            marker = 'OK' if ok else 'FAIL'
            self.stdout.write(f'[{marker}] {name}')
            if not ok:
                failed.append(name)

        if failed:
            raise CommandError(f'测试数据校验失败: {", ".join(failed)}')

        self.stdout.write(self.style.SUCCESS(f'测试数据校验通过 (profile={profile})'))
