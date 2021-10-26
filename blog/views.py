from rest_framework.generics import ListAPIView, CreateAPIView

from blog.models import Blog, Comment
from blog.serializers import BlogSerializer, CommentSerializer


class BlogAPIView(ListAPIView, CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class CommentAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
