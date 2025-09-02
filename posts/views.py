from django.core.exceptions import PermissionDenied
from django.urls import reverse
from rest_framework import viewsets, status, serializers
from .models import Post, SubPost
from interactions.models import Like
from .serializers import PostSerializer, SubPostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import AnonymousUser
from django.views.generic import ListView, DetailView, UpdateView
from .forms import PostForm, SubPostFormSet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import F
import logging

logger = logging.getLogger(__name__)


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.all().select_related('author').order_by('-created_at')



class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.prefetch_related('subposts', 'likes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        if self.request.user.is_authenticated:
            context['user_liked'] = post.likes.filter(user=self.request.user).exists()
        else:
            context['user_liked'] = False

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.views_count = F('views_count') + 1
        obj.save(update_fields=['views_count'])
        obj.refresh_from_db()
        return obj



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['subpost_formset'] = SubPostFormSet(self.request.POST)
        else:
            context['subpost_formset'] = SubPostFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['subpost_formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.save()

            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не можете редактировать этот пост")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['subpost_formset'] = SubPostFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['subpost_formset'] = SubPostFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['subpost_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.prefetch_related("subposts").order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете редактировать этот пост")
        serializer.save()

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

        try:
            with transaction.atomic():
                like, created = Like.objects.get_or_create(user=request.user, post=post)
                like_count = Like.objects.filter(post=post).count()

                if not created:
                    like.delete()
                    like_count = Like.objects.filter(post=post).count()
                    post.like_count = like_count
                    post.save(update_fields=["like_count"])
                    return Response({
                        "status": "unliked",
                        "like_count": like_count
                    }, status=status.HTTP_200_OK)
                else:
                    post.like_count = like_count
                    post.save(update_fields=["like_count"])
                    return Response({
                        "status": "liked",
                        "like_count": like_count
                    }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in like action: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                # Проверка обязательных полей
                if 'title' not in item or 'body' not in item:
                    continue

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
                    # Проверка полей подпоста
                    if 'title' in subpost_data and 'body' in subpost_data:
                        SubPost.objects.create(
                            title=subpost_data["title"],
                            body=subpost_data["body"],
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
                        if 'title' in sp_data and 'body' in sp_data:
                            SubPost.objects.create(
                                post=instance,
                                title=sp_data["title"],
                                body=sp_data["body"],
                            )

                to_delete = set(existing_ids) - set(sent_ids)
                if to_delete:
                    SubPost.objects.filter(id__in=to_delete, post=instance).delete()

            return Response(self.get_serializer(instance).data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете редактировать этот пост")
        serializer.save()


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



@require_POST
def post_delete(request, pk):
    from .models import Post
    post = get_object_or_404(Post, id=pk)

    if request.user != post.author:
        return JsonResponse({'error': 'У вас нет прав на удаление этого поста'}, status=403)

    post.delete()
    return JsonResponse({'success': True})