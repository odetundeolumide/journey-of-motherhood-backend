from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Follow(models.Model):
    followers = models.ForeignKey(User, related_name='followings', on_delete=models.CASCADE, null=True)
    followings = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('followers', 'followings')

    def __str__(self):
        return f'{self.followers} follows {self.followings}'
