from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('post', 'Post Creation'),
        ('user', 'New User Registration'),
        ('quote', 'New Quote'),
        ('follower', 'New Follower'),
        ('comment', 'New Comment'),
        ('reaction', 'New Reaction'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.notification_type} notification for user {self.user.email}"
