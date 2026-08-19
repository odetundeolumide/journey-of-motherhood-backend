from django.urls import path
from .views import FollowCreateAPIView, FollowDeleteAPIView

app_name = 'follow'

urlpatterns = [
    path('<int:user_id>/', FollowCreateAPIView.as_view(), name='follow'),
    path('unfollow/<int:user_id>/', FollowDeleteAPIView.as_view(), name='unfollow'),
]
