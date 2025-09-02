from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from posts.views import (PostViewSet, SubPostViewSet, PostListView, PostDetailView,
                         PostCreateView, PostUpdateView, post_delete)
from accounts.views import SignUpView, MyPostsListView
from interactions.views import (CommentViewSet, FavoriteViewSet,
                               comment_delete, FavoritesListView)
from notifications.views import InboxView, NotificationMarkAsReadView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static


# Создаем роутер для API
router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"subposts", SubPostViewSet, basename="subpost")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"favorites", FavoriteViewSet, basename="favorite")
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', CommentViewSet, basename='post-comments')

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
    path("api/", include(posts_router.urls)),

    # Аутентификация JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Документация
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Аутентификация для фронтенда
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='posts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Фронтенд URLs
    path('', PostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('my-posts/', MyPostsListView.as_view(), name='my_posts'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
    path('comments/delete/<int:pk>/', comment_delete, name='comment_delete'),
    path('posts/<int:pk>/delete/', post_delete, name='post_delete'),
    path('api/notifications/<int:pk>/mark_read/', NotificationMarkAsReadView.as_view(), name='notification_mark_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)