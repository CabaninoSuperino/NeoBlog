from rest_framework import serializers
from .models import Comment, Favorite

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Проверка что текст комментария не пустой
        """
        if not data.get('text', '').strip():
            raise serializers.ValidationError({"text": "Комментарий не может быть пустым"})
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    author_username = serializers.CharField(source='post.author.username', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'post', 'post_title', 'author_username', 'created_at']
        read_only_fields = ['id', 'created_at']