from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Follow
from rest_framework.permissions import IsAuthenticated
from UserProfile.models import CustomUser
from .serializers import FollowSerializer
from rest_framework.views import APIView


class FollowCreateAPIView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['follower'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class FollowDeleteAPIView(generics.DestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Follow.objects.get(
            followers=self.request.user,
            followings=self.kwargs['user_id'],
            followers__id=self.request.user.id
        )


    def perform_destroy(self, instance):
        instance.delete()

