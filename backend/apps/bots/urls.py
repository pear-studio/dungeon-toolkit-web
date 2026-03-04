from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.BotRegistrationView.as_view(), name='bot-register'),
    path('heartbeat/', views.BotHeartbeatView.as_view(), name='bot-heartbeat'),
    path('bind/', views.BotBindView.as_view(), name='bot-bind'),
    path('', views.BotListView.as_view(), name='bot-list'),
    path('my/', views.MyBotListView.as_view(), name='bot-my-list'),
    path('<uuid:pk>/regenerate-key/', views.BotRegenerateKeyView.as_view(), name='bot-regenerate-key'),
    path('<uuid:id>/', views.BotDetailView.as_view(), name='bot-detail'),
    path('<uuid:id>/update/', views.BotUpdateView.as_view(), name='bot-update'),
    path('<uuid:id>/delete/', views.BotDeleteView.as_view(), name='bot-delete'),
]
