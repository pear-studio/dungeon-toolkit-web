from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """服务健康检查"""
    return Response({'status': 'ok', 'service': 'DNDChar API'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health'),
    path('api/auth/', include('apps.users.urls')),
    path('api/characters/', include('apps.characters.urls')),
    path('api/gamedata/', include('apps.gamedata.urls')),
    path('api/rules/', include('apps.rules.urls')),
    path('api/aigc/', include('apps.aigc.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
