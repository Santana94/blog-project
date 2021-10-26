import json

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from model_bakery import baker

from blog.models import Blog


class TestBlog(APITestCase):

    def setUp(self):
        self.blog_url = reverse('blog:blog-view')

    def test_blog_list_endpoint(self):
        blogs = baker.make("blog.blog", _quantity=10)

        response = self.client.get(self.blog_url)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_data,
            [
                {
                    "id": blog.id,
                    "created_at": blog.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "title": blog.title,
                    "description": blog.description,
                }
                for blog in sorted(blogs, key=lambda x: x.id)
            ]
        )

    def test_blog_list_endpoint_returns_empty_list(self):
        response = self.client.get(self.blog_url)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, [])

    def test_blog_create_endpoint(self):
        self.assertEqual(Blog.objects.count(), 0)
        data = {
            'title': 'My Blog Title',
            'description': 'My blog description with lots of information'
        }
        response = self.client.post(self.blog_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Blog.objects.count(), 1)

    def test_blog_create_endpoint_without_title(self):
        self.assertEqual(Blog.objects.count(), 0)
        data = {
            'description': 'My blog description with lots of information'
        }
        response = self.client.post(self.blog_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
