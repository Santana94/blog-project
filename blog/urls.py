from django.urls import path

from blog.views import BlogAPIView, CommentAPIView

app_name = "blog"

urlpatterns = [
    path('blog/', BlogAPIView.as_view(), name="blog-view"),
    path('comment/', CommentAPIView.as_view(), name="comment-view")
]
