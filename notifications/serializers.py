from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    post_title = serializers.SerializerMethodField()
    comment_text = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type',
            'post', 'post_title', 'comment', 'comment_text',
            'created_at', 'is_read'
        ]
        read_only_fields = fields

    def get_post_title(self, obj):
        return obj.post.title if obj.post else None

    def get_comment_text(self, obj):
        if obj.comment:
            return obj.comment.text[:100] + '...' if len(obj.comment.text) > 100 else obj.comment.text
        return None