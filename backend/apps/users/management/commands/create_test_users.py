from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '创建测试账号'

    def handle(self, *args, **options):
        users = [
            {
                'username': 'testuser',
                'email': 'test@dungeon-toolkit.local',
                'password': 'TestPass1234',
                'is_staff': False,
                'is_superuser': False,
                'description': '通用测试账号',
            },
            {
                'username': 'admin',
                'email': 'admin@dungeon-toolkit.local',
                'password': 'AdminPass1234',
                'is_staff': True,
                'is_superuser': True,
                'description': '管理员账号',
            },
            {
                'username': 'runner',
                'email': 'runner@dungeon-toolkit.local',
                'password': 'RunnerPass1234',
                'is_staff': False,
                'is_superuser': False,
                'description': 'CI/CD 测试账号',
            },
        ]

        for u in users:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email = u['email']
            user.set_password(u['password'])
            user.is_staff = u.get('is_staff', False)
            user.is_superuser = u.get('is_superuser', False)
            user.save()

            status = '创建' if created else '更新'
            self.stdout.write(f'{status}: {u["username"]} ({u["description"]})')

        self.stdout.write(self.style.SUCCESS('\n测试账号创建完成！'))
        self.stdout.write('-' * 50)
        self.stdout.write('测试账号信息:')
        self.stdout.write(f'  testuser / TestPass1234  (通用测试)')
        self.stdout.write(f'  admin   / AdminPass1234  (管理员)')
        self.stdout.write(f'  runner  / RunnerPass1234  (CI/CD)')
