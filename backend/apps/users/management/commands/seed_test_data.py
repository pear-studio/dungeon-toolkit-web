import hashlib

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.bots.models import Bot

User = get_user_model()


FIXTURE_USERS = [
    {
        'username': 'fixture_normal',
        'email': 'fixture_normal@dungeon-toolkit.local',
        'password': 'FixturePass1234',
        'description': '正常登录场景用户',
    },
    {
        'username': 'fixture_expired',
        'email': 'fixture_expired@dungeon-toolkit.local',
        'password': 'FixturePass1234',
        'description': 'access 过期恢复场景用户',
    },
    {
        'username': 'fixture_refresh_fail',
        'email': 'fixture_refresh_fail@dungeon-toolkit.local',
        'password': 'FixturePass1234',
        'description': 'refresh 失败场景用户',
    },
]

FIXTURE_BOTS = [
    {
        'bot_id': '880001',
        'nickname': 'Alpha Scout',
        'master_username': 'fixture_normal',
        'master_qq': '10001',
        'version': 'v1.0.0',
        'description': '[MOCK] keyword-alpha online sample',
        'is_public': True,
        'status': 'online',
    },
    {
        'bot_id': '880002',
        'nickname': 'Beta Watcher',
        'master_username': 'fixture_normal',
        'master_qq': '10001',
        'version': 'v1.0.1',
        'description': '[MOCK] keyword-beta offline sample',
        'is_public': True,
        'status': 'offline',
    },
    {
        'bot_id': '880003',
        'nickname': 'Gamma Lens',
        'master_username': 'fixture_expired',
        'master_qq': '10002',
        'version': 'v1.1.0',
        'description': '[MOCK] keyword-gamma online sample',
        'is_public': True,
        'status': 'online',
    },
    {
        'bot_id': '880004',
        'nickname': 'Delta Private',
        'master_username': 'fixture_refresh_fail',
        'master_qq': '10003',
        'version': 'v1.2.0',
        'description': '[MOCK] private fixture for ownership checks',
        'is_public': False,
        'status': 'offline',
    },
    {
        'bot_id': '880005',
        'nickname': 'Echo Empty',
        'master_username': 'fixture_normal',
        'master_qq': '10001',
        'version': 'v1.3.0',
        'description': '[MOCK] keyword-empty boundary sample',
        'is_public': True,
        'status': 'unknown',
    },
]

PROFILE_CHOICES = ['baseline', 'empty-robot-plaza']


def _fixture_api_key(bot_id: str) -> str:
    return hashlib.sha256(f'fixture:{bot_id}'.encode('utf-8')).hexdigest()


def get_fixture_usernames():
    return [u['username'] for u in FIXTURE_USERS]


def get_fixture_bot_ids():
    return [b['bot_id'] for b in FIXTURE_BOTS]


def build_validation_checks(profile: str):
    checks = []

    checks.append((
        'fixture users present',
        User.objects.filter(username__in=get_fixture_usernames()).count() == len(FIXTURE_USERS),
    ))

    checks.append((
        'fixture bots present',
        Bot.objects.filter(bot_id__in=get_fixture_bot_ids()).count() == len(FIXTURE_BOTS),
    ))

    if profile == 'baseline':
        checks.append((
            'public bots available for plaza',
            Bot.objects.filter(bot_id__in=get_fixture_bot_ids(), is_public=True).exists(),
        ))
        checks.append((
            'contains both online/offline statuses',
            Bot.objects.filter(bot_id__in=get_fixture_bot_ids(), status='online').exists()
            and Bot.objects.filter(bot_id__in=get_fixture_bot_ids(), status='offline').exists(),
        ))
    else:
        checks.append((
            'robot plaza can be empty',
            not Bot.objects.filter(bot_id__in=get_fixture_bot_ids(), is_public=True).exists(),
        ))

    return checks


class Command(BaseCommand):
    help = '初始化可重复测试数据（固定账号 + 机器人夹具）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            choices=PROFILE_CHOICES,
            default='baseline',
            help='baseline: 标准测试数据；empty-robot-plaza: 机器人广场空数据模式',
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            help='若核心夹具校验失败则返回非零退出码',
        )

    def handle(self, *args, **options):
        profile = options['profile']
        strict = options['strict']

        users_by_username = self._seed_users()
        self._seed_bots(users_by_username, profile=profile)

        checks = build_validation_checks(profile=profile)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('测试数据初始化完成'))
        self.stdout.write(f'- profile: {profile}')
        for check_name, ok in checks:
            marker = 'OK' if ok else 'FAIL'
            self.stdout.write(f'  [{marker}] {check_name}')

        if strict and not all(ok for _, ok in checks):
            raise CommandError('严格模式校验失败，请检查 seed 输出。')

    def _seed_users(self):
        users_by_username = {}
        for user_data in FIXTURE_USERS:
            user, created = User.objects.get_or_create(username=user_data['username'])
            user.email = user_data['email']
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.set_password(user_data['password'])
            user.save()
            users_by_username[user.username] = user

            status_text = '创建' if created else '更新'
            self.stdout.write(f'{status_text}用户: {user.username} ({user_data["description"]})')
        return users_by_username

    def _seed_bots(self, users_by_username, profile: str):
        for bot_data in FIXTURE_BOTS:
            owner = users_by_username[bot_data['master_username']]
            defaults = {
                'nickname': bot_data['nickname'],
                'master': owner,
                'master_qq': bot_data['master_qq'],
                'version': bot_data['version'],
                'description': bot_data['description'],
                'api_key': _fixture_api_key(bot_data['bot_id']),
                'is_public': bot_data['is_public'],
                'status': bot_data['status'],
            }
            bot, created = Bot.objects.update_or_create(
                bot_id=bot_data['bot_id'],
                defaults=defaults,
            )
            status_text = '创建' if created else '更新'
            self.stdout.write(f'{status_text}机器人: {bot.bot_id} ({bot.nickname})')

        if profile == 'empty-robot-plaza':
            updated_count = Bot.objects.filter(bot_id__in=get_fixture_bot_ids()).update(is_public=False)
            self.stdout.write(f'应用空广场模式: 将 {updated_count} 条夹具机器人设为私有')
