from django.db import models
from django.contrib.auth import get_user_model
from interactions.models import Post, Comment


User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('comment_post', 'Комментарий к посту'),
        ('reply_comment', 'Ответ на комментарий'),
        ('like_post', 'Лайк поста'),
        ('like_comment', 'Лайк комментария'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    parent_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notification_parent_comments')

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.get_notification_type_display()}"