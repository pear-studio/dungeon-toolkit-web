from rest_framework import authentication, exceptions
from apps.bots.models import Bot


class BotAuthentication(authentication.BaseAuthentication):
    """
    API Key 认证类
    使用 X-API-Key 头部传递 API Key
    """

    keyword = 'X-API-Key'

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword)
        if not api_key:
            return None

        try:
            bot = Bot.objects.get(api_key=api_key)
        except Bot.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key')

        if not bot.is_public:
            raise exceptions.AuthenticationFailed('Bot is not public')

        return (bot, None)

    def authenticate_header(self, request):
        return self.keyword
