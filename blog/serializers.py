from rest_framework import serializers

from blog.models import Comment, Blog


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'content', 'blog']


class BlogSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False)

    class Meta:
        model = Blog
        fields = ['id', 'created_at', 'title', 'description', 'image']

    def validate_image(self, uploaded_file):
        if uploaded_file is not None:
            return uploaded_file.read()

        return

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = str(instance.image)
        return representation
