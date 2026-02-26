from rest_framework.routers import DefaultRouter
from .views import RulesetViewSet, RaceViewSet, CharClassViewSet, BackgroundViewSet, SpellViewSet

router = DefaultRouter()
router.register(r'rulesets', RulesetViewSet, basename='ruleset')
router.register(r'races', RaceViewSet, basename='race')
router.register(r'classes', CharClassViewSet, basename='charclass')
router.register(r'backgrounds', BackgroundViewSet, basename='background')
router.register(r'spells', SpellViewSet, basename='spell')

urlpatterns = router.urls