from .models import Favorite, Comment
from interactions.serializers import FavoriteSerializer, CommentSerializer
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from posts.models import Post
from interactions.models import Like
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect



class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user,
            post__isnull=False
        ).select_related('post__author')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Like
    template_name = 'posts/favorites.html'
    context_object_name = 'likes'

    def get_queryset(self):
        qs = Like.objects.filter(
            user=self.request.user,
            post__isnull=False
        ).select_related('post__author')

        print(f"Запрос лайков для {self.request.user}: {qs.count()} результатов")
        for like in qs:
            print(f" - {like.post.title if like.post else 'No post'}")
        return qs


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # Логируем ошибку для диагностики
            print(f"Error creating comment: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return super().get_permissions()


def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        raise PermissionDenied("Вы не можете удалить этот комментарий")
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)




