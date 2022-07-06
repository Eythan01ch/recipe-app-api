"""
Tests for the Tag API
"""

from core.models import Tag, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

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

	def test_filter_tag_assigned_to_recipe(self):
		"""
		We create two tags, one of which is assigned to a recipe.
		We then make a request to the tags endpoint with the assigned_only parameter set to 1.
		We then check that the response contains the tag that is assigned to the recipe, but not the other one
		"""

		tag1 = Tag.objects.create(user=self.user, name='Ew')
		tag2 = Tag.objects.create(user=self.user, name='Yum')

		re1 = Recipe.objects.create(
			user=self.user,
			title='Yum Food',
			time_minutes='12',
			price=Decimal('12.22'),
		)
		re1.tags.add(tag1)

		response = self.client.get(TAGS_URL, {'assigned_only': 1})
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		s1 = TagSerializer(tag1)
		s2 = TagSerializer(tag2)
		"""
		We create two recipes, both with the same tag. 
		
		We then make a request to the API with the assigned_only parameter set to 1. 
		
		We expect the response to contain only one tag. 
		
		The reason is that the assigned_only parameter should filter out duplicate tags. 
		
		Let's run the test and see what happens. 
		
		$ python manage.py test app.recipe.tests.test_tags_api
		Creating test database for alias 'default'...
		System check identified no issues (0 silenced).
		F
		======================================================================
		FAIL: test_filter_tags_unique (app.recipe.tests.test_tags_api.PublicTagsApiTests)
		----------------------------------------------------------------------
		Traceback (most recent call last):
		  File "/code/app/recipe/tests/test_tags_api.py", line 81, in test_filter_tags
		"""

		self.assertIn(s1.data, response.data)
		self.assertNotIn(s2.data, response.data)

	def test_filter_tags_unique(self):
		"""
		We create two tags, one recipe with one tag, and another recipe with the same tag.
		We then make a request to the API with the assigned_only parameter set to 1.
		We expect the response to be 200 OK, and the length of the response data to be 1.
		This is because we expect the API to return only one tag, the one that is assigned to both recipes.
		"""

		tag1 = Tag.objects.create(user=self.user, name='bad')
		Tag.objects.create(user=self.user, name='good')

		re1 = Recipe.objects.create(
			user=self.user,
			title='Egg Food',
			time_minutes='12',
			price=Decimal('12.22'),
		)
		re2 = Recipe.objects.create(
			user=self.user,
			title='Egg Cool',
			time_minutes='12',
			price=Decimal('12.22'),
		)
		re1.tags.add(tag1)
		re2.tags.add(tag1)


		response = self.client.get(TAGS_URL, {'assigned_only': 1})
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assertEqual(len(response.data), 1)
