from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkAsReadView,
    NotificationMarkSingleAsReadView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('mark-as-read/', NotificationMarkAsReadView.as_view(), name='notification_mark_as_read'),
    path('mark-single-as-read/<int:notification_id>/', NotificationMarkSingleAsReadView.as_view(), name='notification_mark_single_as_read'),
]
