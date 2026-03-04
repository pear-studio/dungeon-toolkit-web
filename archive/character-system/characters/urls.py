from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CharacterViewSet, CharacterPublicView

router = DefaultRouter()
router.register(r'', CharacterViewSet, basename='character')
router.register(r'public', CharacterPublicView, basename='character-public')

urlpatterns = router.urls