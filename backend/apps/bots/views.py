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


class BotBindView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bot_id = request.data.get('bot_id')
        if not bot_id:
            return Response(
                {'bot_id': '请输入机器人QQ号'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            bot = Bot.objects.get(bot_id=bot_id)
        except Bot.DoesNotExist:
            return Response(
                {'detail': '机器人不存在，请确保机器人已通过注册API登记'},
                status=status.HTTP_404_NOT_FOUND
            )

        if bot.master == request.user:
            return Response(
                {'detail': '你已经绑定了这个机器人'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bot.master = request.user
        bot.save()

        return Response({'message': '绑定成功'})


class BotRegenerateKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            bot = Bot.objects.get(pk=pk, master=request.user)
        except Bot.DoesNotExist:
            return Response(
                {'detail': '机器人不存在或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )

        bot.api_key = secrets.token_hex(32)
        bot.save()

        return Response({'api_key': bot.api_key})


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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BotSerializer
        return BotSerializer


class BotDetailView(generics.RetrieveAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


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


class MyBotListView(generics.ListAPIView):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(master=self.request.user)
