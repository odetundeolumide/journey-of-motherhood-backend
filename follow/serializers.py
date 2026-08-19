from rest_framework import serializers
from .models import Follow

class FollowSerializer(serializers.ModelSerializer):
    followers = serializers.ReadOnlyField(source='followers.email')
    followings = serializers.ReadOnlyField(source='followings.email')

    class Meta:
        model = Follow
        fields = ('id', 'followers', 'followings', 'created_at')
