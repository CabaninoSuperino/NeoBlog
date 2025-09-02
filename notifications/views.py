from rest_framework import viewsets, status
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView


class NotificationMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.is_read = True
            notification.save()
            return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class InboxView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'posts/inbox.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).update(is_read=True)

        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'sender', 'post', 'comment', 'parent_comment', 'post__author'
        ).order_by('-created_at')

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).update(is_read=True)

        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'sender', 'post', 'comment'
        ).order_by('-created_at')