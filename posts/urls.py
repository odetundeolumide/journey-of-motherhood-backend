
from django.urls import path
from .views import CommentCreateView, CommentListView, NewPostsView, PostCreateAPIView, PostDeleteAPIView, PostDetailAPIView, PostListAPIView, PostSearchAPIView, PostTopicFilterView, PostUpdateAPIView, PopularTopicsView, ReactionCreateView, ReactionListView, TrendingPostsView


urlpatterns = [
    path('<int:post_id>/reaction/',
         ReactionCreateView.as_view(), name="reaction_post"),
    path('reaction/<int:post_id>/',
         ReactionListView.as_view(), name="reaction_list"),
    path('<int:post_id>/comment/', CommentCreateView.as_view(), name='comment_post'),
    path('comment/<int:post_id>/', CommentListView.as_view(), name='list_comment'),
    path('all/', PostListAPIView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailAPIView.as_view(), name='post-detail'),
    path('create/', PostCreateAPIView.as_view(), name='post-create'),
    path('<int:pk>/update/', PostUpdateAPIView.as_view(), name='post-update'),
    path('<int:pk>/delete/', PostDeleteAPIView.as_view(), name='post-delete'),
    path('search/', PostSearchAPIView.as_view(), name='post-search'),
    path('popular/', PopularTopicsView.as_view(), name='popular-topics'),
    path('trending/', TrendingPostsView.as_view(), name='trending_posts'),
    path('new/', NewPostsView.as_view(), name='new_posts'),
    path('topic/<str:topic>/', PostTopicFilterView.as_view(), name="post-topic-filter")
]
