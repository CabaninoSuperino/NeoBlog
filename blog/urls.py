from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from posts.views import PostViewSet, SubPostViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Создаем роутер для API
router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"subposts", SubPostViewSet, basename="subpost")


# View для корня API
@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "posts": reverse("post-list", request=request, format=format),
            "subposts": reverse("subpost-list", request=request, format=format),
            "swagger": reverse("swagger-ui", request=request, format=format),
        }
    )


urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),
    # Корень API
    path("api/", api_root, name="api-root"),
    # Основные API endpoints
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Документация
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
