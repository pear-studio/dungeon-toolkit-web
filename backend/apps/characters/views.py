from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Character
from .serializers import (
    CharacterListSerializer,
    CharacterDetailSerializer,
    CharacterCreateSerializer,
    CharacterPublicSerializer,
)


class CharacterViewSet(viewsets.ModelViewSet):
    """
    角色 CRUD：
      GET    /api/characters/          - 我的角色列表
      POST   /api/characters/          - 创建角色（向导提交）
      GET    /api/characters/{id}/     - 角色详情
      PATCH  /api/characters/{id}/     - 更新角色
      DELETE /api/characters/{id}/     - 删除角色
      POST   /api/characters/{id}/share/  - 切换公开状态
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Character.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CharacterCreateSerializer
        if self.action in ('list',):
            return CharacterListSerializer
        return CharacterDetailSerializer

    @action(detail=True, methods=['post'], url_path='share')
    def toggle_share(self, request, pk=None):
        """切换角色公开分享状态"""
        character = self.get_object()
        character.is_public = not character.is_public
        character.save(update_fields=['is_public'])
        return Response({
            'is_public': character.is_public,
            'share_token': str(character.share_token),
        })


class CharacterPublicView(viewsets.GenericViewSet):
    """
    公开分享页（无需登录）:
      GET /api/characters/public/{share_token}/
    """
    permission_classes = [AllowAny]
    serializer_class = CharacterPublicSerializer

    @action(detail=False, methods=['get'], url_path=r'(?P<token>[0-9a-f-]+)')
    def retrieve_by_token(self, request, token=None):
        character = get_object_or_404(Character, share_token=token, is_public=True)
        serializer = self.get_serializer(character)
        return Response(serializer.data)
