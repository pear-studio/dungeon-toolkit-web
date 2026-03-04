from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import secrets

from .models import Bot
from .serializers import (
    BotSerializer, BotRegistrationSerializer, BotHeartbeatSerializer
)
from .authentication import BotAuthentication


class BotRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BotRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        bot_id = data['bot_id']

        bot = Bot.objects.filter(bot_id=bot_id).first()
        if bot:
            bot.nickname = data['nickname']
            bot.master_qq = data['master_id']
            bot.version = data.get('version', '')
            bot.description = data.get('description', '')
            bot.api_key = secrets.token_hex(32)
            bot.save()
        else:
            master_qq = data['master_id']
            from apps.users.models import User
            master = User.objects.filter(username=f'qq_{master_qq}').first()
            if not master:
                master = User.objects.create_user(
                    username=f'qq_{master_qq}',
                    email=f'qq_{master_qq}@example.com',
                    password=secrets.token_hex(16)
                )

            bot = Bot.objects.create(
                bot_id=bot_id,
                nickname=data['nickname'],
                master=master,
                master_qq=master_qq,
                version=data.get('version', ''),
                description=data.get('description', ''),
                api_key=secrets.token_hex(32)
            )

        return Response({
            'bot_id': bot.bot_id,
            'api_key': bot.api_key,
            'nickname': bot.nickname
        }, status=status.HTTP_201_CREATED)


class BotHeartbeatView(APIView):
    authentication_classes = [BotAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        bot = request.user
        if not bot or not isinstance(bot, Bot):
            return Response(
                {'error': 'Invalid API Key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = BotHeartbeatSerializer(data=request.data)
        if serializer.is_valid():
            bot.status = serializer.validated_data.get('status', 'online')
            bot.last_seen = timezone.now()
            bot.save()
            return Response({'status': bot.status})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BotListView(generics.ListCreateAPIView):
    queryset = Bot.objects.filter(is_public=True)
    serializer_class = BotSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class BotDetailView(generics.RetrieveAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class BotCreateView(generics.CreateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class BotUpdateView(generics.UpdateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Bot.objects.filter(master=self.request.user)


class BotDeleteView(generics.DestroyAPIView):
    queryset = Bot.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Bot.objects.filter(master=self.request.user)
