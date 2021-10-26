import json

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status
from model_bakery import baker

from blog.models import Blog, Comment


class TestBlog(APITestCase):

    def setUp(self):
        self.blog_url = reverse('blog:blog-view')

        self.file_content = b"file_content"
        self.image = SimpleUploadedFile("file.png", self.file_content, content_type="image/png")

    def test_blog_list_endpoint(self):
        blogs = baker.make("blog.blog", _quantity=10, image=self.file_content)

        response = self.client.get(self.blog_url)
        response_data = json.loads(response.content)
        expected_blogs_data = [
            {
                "id": blog.id,
                "created_at": blog.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "title": blog.title,
                "description": blog.description,
                "image": str(blog.image),
            }
            for blog in sorted(blogs, key=lambda x: x.id)
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, expected_blogs_data)

    def test_blog_list_endpoint_with_comments(self):
        blogs = baker.make("blog.blog", _quantity=10, image=self.file_content)
        comments = baker.make("blog.comment", _quantity=10, blog__image=self.file_content)
        blogs_with_comments = [i.blog for i in comments]

        response = self.client.get(self.blog_url)
        response_data = json.loads(response.content)
        expected_blogs_data = [
            {
                "id": blog.id,
                "created_at": blog.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "title": blog.title,
                "description": blog.description,
                "image": str(blog.image),
            }
            for blog in sorted([*blogs, *blogs_with_comments], key=lambda x: x.id)
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, expected_blogs_data)

    def test_blog_list_endpoint_returns_empty_list(self):
        response = self.client.get(self.blog_url)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, [])

    def test_blog_create_endpoint(self):
        self.assertEqual(Blog.objects.count(), 0)
        data = {
            'title': 'My Blog Title',
            'description': 'My blog description with lots of information',
            'image': self.image,
        }
        response = self.client.post(self.blog_url, data, format='multipart')
        created_blog = Blog.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_blog.title, data['title'])
        self.assertEqual(created_blog.description, data['description'])
        self.assertEqual(created_blog.image, self.file_content)

    def test_blog_create_endpoint_with_no_image(self):
        self.assertEqual(Blog.objects.count(), 0)
        data = {
            'title': 'My Blog Title',
            'description': 'My blog description with lots of information',
        }
        response = self.client.post(self.blog_url, data, format='multipart')
        created_blog = Blog.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_blog.title, data['title'])
        self.assertEqual(created_blog.description, data['description'])
        self.assertEqual(created_blog.image, None)

    def test_blog_create_endpoint_with_no_title(self):
        data = {
            'description': 'My blog description with lots of information'
        }
        response = self.client.post(self.blog_url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, {"title": ["This field is required."]})

    def test_blog_create_endpoint_with_no_description(self):
        data = {
            'title': 'My Blog Title'
        }
        response = self.client.post(self.blog_url, data, format='json')
        created_blog = Blog.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_blog.title, data['title'])
        self.assertEqual(created_blog.description, None)
        self.assertEqual(created_blog.image, None)

    def test_blog_create_endpoint_wrong_file_format(self):
        data = {
            'title': 'My Blog Title',
            'description': 'My blog description with lots of information',
            'image': "image",
        }
        response = self.client.post(self.blog_url, data, format='multipart')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_data,
            {"image": ['The submitted data was not a file. Check the encoding type on the form.']}
        )


class TestComment(APITestCase):

    def setUp(self):
        self.comment_url = reverse('blog:comment-view')

    def test_comment_post_endpoint(self):
        blog = baker.make("blog.blog")
        self.assertEqual(Comment.objects.count(), 0)
        data = {
            'content': 'My comment content with lots of information',
            'blog': blog.id
        }
        response = self.client.post(self.comment_url, data, format='json')
        created_comment = Comment.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_comment.content, data['content'])

    def test_comment_post_endpoint_with_no_blog_information(self):
        self.assertEqual(Comment.objects.count(), 0)
        data = {
            'content': 'My comment content with lots of information',
        }
        response = self.client.post(self.comment_url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, {"blog": ['This field is required.']})

    def test_comment_post_endpoint_with_invalid_blog_information(self):
        self.assertEqual(Comment.objects.count(), 0)
        invalid_id = 123
        data = {
            'content': 'My comment content with lots of information',
            'blog': invalid_id
        }
        response = self.client.post(self.comment_url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, {"blog": [f'Invalid pk "{invalid_id}" - object does not exist.']})
