from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .permission import IsAuthorOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from posts.models import Post, Reaction, Comment
from .serializers import AnonymousPostSerializer, CommentSerializer, NewPostSerializer, PopularTopicSerializer, PostSerializer, ReactionSerializer, TrendingPostSerializer
from django.db.models import Q, Count

# Create your views here.


class PostPagination(PageNumberPagination):
    page_size = 15
    page_query_param = page_size
    max_page_size = 50


class PostCreateAPIView(CreateAPIView):
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AnonymousPostSerializer
        else:
            return PostSerializer


class PostUpdateAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AnonymousPostSerializer
        else:
            return PostSerializer


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthorOrReadOnly]


class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj


class PostSearchAPIView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination

    # def get_queryset(self):
    #     search_params = self.request.query_params.dict()
    #     queryset = Post.objects.all()
    #     for key, value in search_params.items():
    #         if key in ['page', 'page_size']:
    #             continue
    #         if '__' in key:
    #             key_parts = key.split('__')
    #             key = key_parts[0]
    #             lookup = key_parts[1]
    #         else:
    #             lookup = 'icontains'
    #             key = f'{key}__{lookup}'
    #         filter_kwargs = {key: value}
    #         queryset = queryset.filter(**filter_kwargs)
    #     return queryset

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        queryset = Post.objects.all()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(topic__icontains=search_query)
            )
        return queryset
    
class PostTopicFilterView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        topic = self.kwargs['topic']
        queryset = Post.objects.filter(topic=topic)
        return queryset


class ReactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response({'detail': 'Reaction added.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReactionListView(ListAPIView):
    serializer_class = ReactionSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        queryset = Reaction.objects.filter(post=post_id)
        return queryset


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListView(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        queryset = Comment.objects.filter(post=post_id)
        return queryset


class PopularTopicsView(APIView):
    def get(self, request):
        popular_topics = Post.objects.values('topic').annotate(
            count=Count('id')).order_by('-count')[:10]
        serializer = PopularTopicSerializer(popular_topics, many=True)
        return Response(serializer.data)
class TrendingPostsView(APIView):
    def get(self, request, format=None):
        # Queryset to get trending posts based on views count
        queryset = Post.objects.order_by('-views')[:10]
        serializer = TrendingPostSerializer(queryset, many=True)
        return Response(serializer.data)


class NewPostsView(APIView):
    def get(self, request, format=None):
        # Queryset to get new posts based on created_at field
        queryset = Post.objects.order_by('-created_at')[:10]
        serializer = NewPostSerializer(queryset, many=True)
        return Response(serializer.data)