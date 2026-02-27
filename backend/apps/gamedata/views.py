from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ruleset, Race, CharClass, Background, Spell, Item
from .serializers import (
    RulesetSerializer,
    RaceListSerializer, RaceDetailSerializer,
    CharClassListSerializer, CharClassDetailSerializer,
    BackgroundListSerializer, BackgroundDetailSerializer,
    SpellListSerializer, SpellDetailSerializer,
    ItemListSerializer, ItemDetailSerializer,
)


class RulesetViewSet(viewsets.ReadOnlyModelViewSet):
    """规则集列表（只读）"""
    queryset = Ruleset.objects.filter(is_active=True)
    serializer_class = RulesetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RaceViewSet(viewsets.ReadOnlyModelViewSet):
    """种族列表与详情（只读）"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruleset__slug']

    def get_queryset(self):
        return Race.objects.select_related('ruleset').prefetch_related('subraces').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RaceDetailSerializer
        return RaceListSerializer


class CharClassViewSet(viewsets.ReadOnlyModelViewSet):
    """职业列表与详情（只读）"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruleset__slug', 'is_spellcaster']

    def get_queryset(self):
        return CharClass.objects.select_related('ruleset').prefetch_related('subclasses').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CharClassDetailSerializer
        return CharClassListSerializer


class BackgroundViewSet(viewsets.ReadOnlyModelViewSet):
    """背景列表与详情（只读）"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruleset__slug']

    def get_queryset(self):
        return Background.objects.select_related('ruleset').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BackgroundDetailSerializer
        return BackgroundListSerializer


class SpellViewSet(viewsets.ReadOnlyModelViewSet):
    """法术列表与详情（只读，支持多条件过滤）"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ruleset__slug', 'level', 'school', 'concentration', 'ritual']
    search_fields = ['name', 'name_en']

    def get_queryset(self):
        qs = Spell.objects.select_related('ruleset').all()
        # 支持按职业过滤：?class=wizard
        class_slug = self.request.query_params.get('class')
        if class_slug:
            qs = qs.filter(classes__contains=class_slug)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SpellDetailSerializer
        return SpellListSerializer


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """物品列表与详情（只读）"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruleset__slug', 'category']

    def get_queryset(self):
        return Item.objects.select_related('ruleset').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemListSerializer
