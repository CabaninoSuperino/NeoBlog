from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Like
import secrets

User = get_user_model()


class PostViewSetJWTTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password=secrets.token_urlsafe(8)
        )
        self.user2 = User.objects.create_user(
            username="user2", password=secrets.token_urlsafe(8)
        )
        self.post = Post.objects.create(
            title="Test post", body="Body", author=self.user1
        )
        self.client = APIClient()

        # Получаем токен для user2
        refresh = RefreshToken.for_user(self.user2)
        self.access_token = str(refresh.access_token)

        # Получаем токен для user1 (автора)
        refresh1 = RefreshToken.for_user(self.user1)
        self.access_token1 = str(refresh1.access_token)

    def auth_client(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_posts(self):
        url = reverse("post-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_like_post(self):
        self.auth_client(self.access_token)
        url = reverse("post-like", kwargs={"pk": self.post.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["status"], "liked")
        self.assertTrue(Like.objects.filter(post=self.post, user=self.user2).exists())

    def test_unlike_post(self):
        Like.objects.create(post=self.post, user=self.user2)
        self.auth_client(self.access_token)
        url = reverse("post-like", kwargs={"pk": self.post.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "unliked")
        self.assertFalse(Like.objects.filter(post=self.post, user=self.user2).exists())

    def test_like_own_post_forbidden(self):
        self.auth_client(self.access_token1)  # автор поста
        url = reverse("post-like", kwargs={"pk": self.post.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)
        self.assertIn("You cannot like your own post", resp.data["error"])

    def test_increment_views(self):
        self.auth_client(self.access_token)
        url = reverse("post-view", kwargs={"pk": self.post.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(resp.data["views_count"], self.post.views_count)

    def test_bulk_create_posts_with_subposts(self):
        self.auth_client(self.access_token)

        url = reverse("post-list")
        data = [
            {
                "title": "Bulk post 1",
                "body": "Body 1",
                "subposts": [
                    {"title": "SubPost 1.1", "body": "SubBody 1.1"},
                    {"title": "SubPost 1.2", "body": "SubBody 1.2"},
                ],
            },
            {
                "title": "Bulk post 2",
                "body": "Body 2",
                "subposts": [{"title": "SubPost 2.1", "body": "SubBody 2.1"}],
            },
        ]

        response = self.client.post(url, data, format="json")
        if response.status_code != 201:
            print("Response errors:", response.data)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(response.data), 2)

        posts = Post.objects.filter(title__in=["Bulk post 1", "Bulk post 2"])
        self.assertEqual(posts.count(), 2)

        post1 = posts.get(title="Bulk post 1")
        self.assertEqual(post1.subposts.count(), 2)
        subpost_titles = post1.subposts.values_list("title", flat=True)
        self.assertIn("SubPost 1.1", subpost_titles)
        self.assertIn("SubPost 1.2", subpost_titles)

        post2 = posts.get(title="Bulk post 2")
        self.assertEqual(post2.subposts.count(), 1)
        subpost_titles = post2.subposts.values_list("title", flat=True)
        self.assertIn("SubPost 2.1", subpost_titles)
