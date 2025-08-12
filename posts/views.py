from rest_framework import viewsets, status, serializers
from .models import Post, SubPost, Like
from .serializers import PostSerializer, SubPostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import AnonymousUser


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.prefetch_related("subposts").order_by("-created_at")

    @extend_schema(
        methods=["POST"],
        description="Поставить/убрать лайк",
        responses={
            201: OpenApiResponse(description="Лайк поставлен"),
            200: OpenApiResponse(description="Лайк убран"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        try:
            post = self.get_object()
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if post.author == request.user:
            return Response(
                {"error": "You cannot like your own post"},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
                post.like_count = Like.objects.filter(post=post).count()
                post.save(update_fields=["like_count"])
                return Response({"status": "unliked"}, status=status.HTTP_200_OK)
            else:
                post.like_count = Like.objects.filter(post=post).count()
                post.save(update_fields=["like_count"])
                return Response({"status": "liked"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        methods=["GET"],
        description="Увеличить счетчик просмотров",
        responses={200: OpenApiResponse(description="Счетчик обновлен")},
    )
    @action(detail=True, methods=["get"])
    def view(self, request, pk=None):
        try:
            with transaction.atomic():
                post = Post.objects.select_for_update().get(pk=pk)
                post.views_count = models.F("views_count") + 1
                post.save()
                post.refresh_from_db()
                return Response({"views_count": post.views_count})
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            return self.bulk_create(request, *args, **kwargs)
        return super().create(request, *args, **kwargs)

    def bulk_create(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = [{**item} for item in request.data]

        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        self.perform_bulk_create(serializer, request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_bulk_create(self, serializer, user):
        with transaction.atomic():
            posts = []
            for item in serializer.validated_data:
                post = Post(
                    title=item["title"],
                    body=item["body"],
                    author=user,
                )
                posts.append(post)

            created_posts = Post.objects.bulk_create(posts)

            for post, item in zip(created_posts, serializer.validated_data):
                subposts_data = item.get("subposts", [])
                for subpost_data in subposts_data:
                    SubPost.objects.create(
                        title=subpost_data.get("title", ""),
                        body=subpost_data.get("body", ""),
                        post=post,
                    )

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            data = request.data.copy()
            subposts_data = data.pop("subposts", [])

            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if subposts_data:
                existing_ids = [sp.id for sp in instance.subposts.all()]
                sent_ids = []

                for sp_data in subposts_data:
                    sp_id = sp_data.get("id")
                    if sp_id:
                        sent_ids.append(sp_id)
                        sp_instance = SubPost.objects.filter(
                            id=sp_id, post=instance
                        ).first()
                        if sp_instance:
                            sp_serializer = SubPostSerializer(
                                sp_instance, data=sp_data, partial=True
                            )
                            sp_serializer.is_valid(raise_exception=True)
                            sp_serializer.save()
                    else:
                        SubPost.objects.create(
                            post=instance,
                            title=sp_data.get("title", ""),
                            body=sp_data.get("body", ""),
                        )

                to_delete = set(existing_ids) - set(sent_ids)
                if to_delete:
                    SubPost.objects.filter(id__in=to_delete, post=instance).delete()

            return Response(self.get_serializer(instance).data)


class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all()
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return SubPost.objects.select_related("post").all()

    def perform_create(self, serializer):
        if "post" not in serializer.validated_data:
            raise serializers.ValidationError(
                {"post": ["This field is required."]}, code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
