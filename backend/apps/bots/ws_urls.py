from django.urls import path

from apps.bots.consumers import BotGatewayConsumer, UserChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<uuid:bot_id>/', UserChatConsumer.as_asgi()),
    path('ws/bot/', BotGatewayConsumer.as_asgi()),
]
