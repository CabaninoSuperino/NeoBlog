from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from interactions.models import Comment, Like
from .models import Notification
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        try:
            # Уведомление для автора поста
            if (hasattr(instance, 'post') and
                instance.post and
                instance.post.author != instance.author):
                Notification.objects.create(
                    recipient=instance.post.author,
                    sender=instance.author,
                    notification_type='comment_post',
                    post=instance.post,
                    comment=instance
                )
                logger.info(f"Created comment notification for post {instance.post.id}")

            # Уведомление для автора родительского комментария
            if (hasattr(instance, 'parent_comment') and
                instance.parent_comment and
                instance.parent_comment.author != instance.author):
                Notification.objects.create(
                    recipient=instance.parent_comment.author,
                    sender=instance.author,
                    notification_type='reply_comment',
                    post=instance.post,
                    comment=instance,
                    parent_comment=instance.parent_comment
                )
                logger.info(f"Created reply notification for comment {instance.parent_comment.id}")
        except Exception as e:
            logger.error(f"Error creating comment notification: {str(e)}")

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        try:
            # Уведомление о лайке поста
            if (hasattr(instance, 'post') and
                instance.post and
                instance.post.author != instance.user):
                Notification.objects.create(
                    recipient=instance.post.author,
                    sender=instance.user,
                    notification_type='like_post',
                    post=instance.post
                )
                logger.info(f"Created like notification for post {instance.post.id}")

            # Уведомление о лайке комментария
            if (hasattr(instance, 'comment') and
                instance.comment and
                instance.comment.author != instance.user):
                Notification.objects.create(
                    recipient=instance.comment.author,
                    sender=instance.user,
                    notification_type='like_comment',
                    comment=instance.comment
                )
                logger.info(f"Created like notification for comment {instance.comment.id}")
        except Exception as e:
            logger.error(f"Error creating like notification: {str(e)}")