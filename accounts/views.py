from posts.models import Post
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
import logging
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)



class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'posts/register.html'


class MyPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/my_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).order_by('-created_at')