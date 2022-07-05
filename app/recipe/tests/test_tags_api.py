"""
Tests for the Tag API
"""

from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
	"""Create and return a detail URL"""
	return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='password123'):
	"""Create and returns user"""
	return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITest(TestCase):
	"""Test unauthenticated API Requests"""

	def setUp(self):
		"""
			Set up of Tests
		"""
		self.client = APIClient()

	def test_auth_required(self):
		"""Test auth is required for retrieving tags"""
		response = self.client.get(TAGS_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
	"""Test authenticated API Requests"""

	def setUp(self):
		"""
			Set up of Tests
		"""
		self.user = create_user()
		self.client = APIClient()

		self.client.force_authenticate(self.user)

	def test_retrieve_tags(self):
		"""Test retrieving a list of tags"""
		Tag.objects.create(user=self.user, name='Vegan')
		Tag.objects.create(user=self.user, name='Dessert')

		response = self.client.get(TAGS_URL)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		tags = Tag.objects.all().order_by('-name')
		serializer = TagSerializer(tags, many=True)

		self.assertEqual(response.data, serializer.data)

	def test_tags_limited_to_user(self):
		user2 = create_user(email='user2@example.com')
		Tag.objects.create(user=user2, name='Fruity')
		tag = Tag.objects.create(user=self.user, name='Comfort')

		response = self.client.get(TAGS_URL)

		self.assertEqual(status.HTTP_200_OK, response.status_code)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0].get('name'), tag.name)
		self.assertEqual(response.data[0].get('id'), tag.id)

	def test_update_tag(self):
		"""Test updating a tag"""
		tag = Tag.objects.create(user=self.user, name='After Dinner')
		payload = {'name': 'Dessert'}
		url = detail_url(tag.id)
		response = self.client.patch(url, payload)

		self.assertEqual(status.HTTP_200_OK, response.status_code)

		tag.refresh_from_db()

		self.assertEqual(tag.name, payload.get('name'))

	def test_delete_tag(self):
		"""Test deleting a tag successful"""
		tag = Tag.objects.create(name='Dessert', user=self.user)
		url = detail_url(tag.id)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Tag.objects.filter(id=tag.id).exists())