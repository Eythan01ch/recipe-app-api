"""
Test for recipe API
"""

from decimal import Decimal

from core.models import Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
	"""Create and Return a Recipe detail url"""
	return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
	"""Create and return a sample recipe"""

	defaults = {
		'title':        'Sample recipe title',
		'time_minutes': 22,
		'price':        Decimal('5.50'),
		'description':  'Sample recipe description',
		'link':         'http://example.com/recipe.pdf'
	}
	defaults.update(params)
	recipe = Recipe.objects.create(user=user, **defaults)
	return recipe


def create_user(**params):
	"""Create and return a new user"""
	return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
	"""test unauthenticated user API requests"""

	def setUp(self):
		"""the client for sending requests"""
		self.client = APIClient()

	def test_auth_required(self):
		"""test auth is required to cal API"""
		response = self.client.get(RECIPES_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
	"""test unauthenticated user API requests"""

	def setUp(self):
		"""creating a client for sending requests and user"""
		self.user = create_user(email='test@example.com', password='password123')

		self.client = APIClient()
		self.client.force_authenticate(self.user)

	def test_retrieve_recipes(self):
		"""test retrieving recipes is successful"""
		create_recipe(user=self.user)
		create_recipe(user=self.user)
		response = self.client.get(RECIPES_URL)

		recipes = Recipe.objects.all().order_by('-id')
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, serializer.data)

	def test_recipe_list_limited_to_user(self):
		"""Test list of recipes is limited to the authenticated user"""

		other_user = create_user(email='other@example.com', password='password123')

		create_recipe(user=other_user)
		create_recipe(user=self.user)

		response = self.client.get(RECIPES_URL)
		recipes = Recipe.objects.filter(user=self.user)
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, serializer.data)

	def test_get_recipe_detail(self):
		"""Test Get recipe details."""
		recipe = create_recipe(user=self.user)
		url = detail_url(recipe.id)

		response = self.client.get(url)
		serializer = RecipeDetailSerializer(recipe)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, serializer.data)

	def test_create_recipe(self):
		"""Test Creating a recipe"""
		payload = {
			'title':        'Sample recipe title',
			'time_minutes': 22,
			'price':        Decimal('5.50'),
			'description':  'Sample recipe description',
			'link':         'http://example.com/recipe.pdf'
		}
		response = self.client.post(RECIPES_URL, payload)  # /api/recipes/recipe/

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		recipe = Recipe.objects.get(id=response.data['id'])

		self.assertEqual(recipe.user, self.user)

		for k, v in payload.items():
			self.assertEqual(getattr(recipe, k), v)

	def test_partial_update(self):
		"""Test Updating a recipe"""

		original_link = 'http://example.com/recipe.pdf'

		recipe = create_recipe(
			user=self.user,
			title='Sample recipe title',
			link=original_link,
		)

		payload = {'title': 'New Sample title'}
		url = detail_url(recipe.id)
		response = self.client.patch(url, payload)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		recipe.refresh_from_db()

		self.assertEqual(recipe.title, payload.get('title'))
		self.assertEqual(recipe.link, original_link)
		self.assertEqual(recipe.user, self.user)

	def test_full_update(self):
		"""Test Full update of a recipe"""

		recipe = create_recipe(
			user=self.user,
			title='Sample recipe title',
			link='http://example.com/recipe.pdf',
			description='Sample recipe description'
		)

		payload = {

			'title':        'New recipe title',
			'link':         'http://example.com/new-recipe.pdf',
			'description':  'New recipe description',
			'time_minutes': 10,
			'price':        Decimal('2.50'),

		}

		url = detail_url(recipe.id)
		response = self.client.put(url, payload)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(recipe.user, self.user)
		recipe.refresh_from_db()

		for k, v in payload.items():
			self.assertEqual(getattr(recipe, k), v)

	def test_update_user_returns_error(self):
		"""Test Changing User will return Error """

		new_user = create_user(email='other@example.com', password='password1')
		recipe = create_recipe(user=self.user)
		payload = {'user': new_user.id}
		url = detail_url(recipe.id)

		self.client.patch(url, payload)

		recipe.refresh_from_db()

		self.assertEqual(recipe.user, self.user)

	def test_delete_recipe(self):
		"""Test deletion of recipe successful"""

		recipe = create_recipe(user=self.user)
		url = detail_url(recipe.id)
		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

	def test_delete_other_user_recipe_error(self):
		"""Test trying to delete another user creates error"""
		new_user = create_user(email='newuser@example.com', password='password123')
		recipe = create_recipe(user=new_user)

		url = detail_url(recipe.id)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

	def test_create_recipe_with_new_tags(self):
		"""Test creating a recipe with new tags"""

		payload = {
			'title':        'Thai Prawn Curry',
			'time_minutes': 30,
			'price':        Decimal('0.50'),
			'tags':         [
				{'name': 'Thai'},
				{'name': 'Dinner'},
			]
		}
		response = self.client.post(RECIPES_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		recipes = Recipe.objects.filter(user=self.user)
		self.assertEqual(recipes.count(), 1)
		recipe = recipes[0]
		self.assertEqual(recipe.tags.count(), 2)

		for tag in payload['tags']:
			exists = recipe.tags.filter(
				name=tag['name'],
				user=self.user
			).exists()
			self.assertTrue(exists)

	def test_create_recipe_with_existing_tags(self):
		"""Test creating a recipe with existing tags """
		tag_indian = Tag.objects.create(name='Indian', user=self.user)

		payload = {
			'title':        'Pongal',
			'time_minutes': 60,
			'price':        Decimal('1.50'),
			'tags':         [
				{'name': 'Indian'},
				{'name': 'Breakfast'}
			]
		}
		response = self.client.post(RECIPES_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		recipes = Recipe.objects.filter(user=self.user)
		self.assertEqual(recipes.count(), 1)
		recipe = recipes[0]
		self.assertEqual(recipe.tags.count(), 2)
		self.assertIn(tag_indian, recipe.tags.all())

		for tag in payload['tags']:
			exists = recipe.tags.filter(
				name=tag['name'],
				user=self.user
			).exists()
			self.assertTrue(exists)

	def test_create_tag_on_update(self):
		"""Test creating a tag when updating a recipe"""
		recipe = create_recipe(user=self.user)

		payload = {'tags': [{'name': 'Lunch'}]}
		url = detail_url(recipe.id)

		response = self.client.patch(url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		new_tag = Tag.objects.get(user=self.user, name='Lunch')
		self.assertIn(new_tag, recipe.tags.all())

	def test_update_recipe_assign_tag(self):
		"""Test assigning an existing tag to a recipe when updating"""
		tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
		recipe = create_recipe(user=self.user)
		recipe.tags.add(tag_breakfast)

		tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

		payload = {
			'tags': [
				{'name': 'Lunch'}
			]
		}
		url = detail_url(recipe.id)
		response = self.client.patch(url, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn(tag_lunch, recipe.tags.all())
		self.assertNotIn(tag_breakfast, recipe.tags.all())

	def test_clear_recipe_tags(self):
		tag = Tag.objects.create(user=self.user, name='Dessert')
		recipe = create_recipe(user=self.user)
		recipe.tags.add(tag)

		url = detail_url(recipe.id)
		payload = {
			'tags': []
		}
		response = self.client.patch(url, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(recipe.tags.count(), 0)

	def test_create_recipe_with_new_ingredients(self):
		"""
		We're creating a recipe with new ingredients, and we're asserting that the recipe was created, and that the ingredients
		were created and associated with the recipe
		"""

		payload = {
			"title":        'Cauliflower',
			'time_minutes': 60,
			'price':        Decimal('10.80'),
			'ingredients':  [
				{'name': 'Cauliflower'},
				{'name': 'Salt'},
				{'name': 'Pepper'},
			],
		}

		response = self.client.post(RECIPES_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		recipes = Recipe.objects.filter(user=self.user)
		self.assertEqual(recipes.count(), 1)
		recipe = recipes[0]

		self.assertEqual(recipe.ingredients.count(), 3)

		# It's checking that the ingredients were created and associated with the recipe.
		for ingredient in payload['ingredients']:
			exists = recipe.ingredients.filter(
				name=ingredient['name'],
				user=self.user,
			).exists()
			self.assertTrue(exists)

	def test_create_recipe_with_existing_ingredients(self):

		ingredient = Ingredient.objects.create(user=self.user, name='Lemon')

		payload = {
			"title":        'Weird Blueberry',
			'time_minutes': 12,
			'price':        Decimal('3.10'),
			'ingredients':  [
				{'name': 'Blueberry'},
				{'name': 'Lemon'},
			],
		}

		response = self.client.post(RECIPES_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		recipes = Recipe.objects.filter(user=self.user)
		self.assertEqual(recipes.count(), 1)
		recipe = recipes[0]

		self.assertEqual(recipe.ingredients.count(), 2)
		self.assertIn(ingredient, recipe.ingredients.all())
		for ingredient in payload['ingredients']:
			exists = recipe.ingredients.filter(
				name=ingredient['name'],
				user=self.user,
			).exists()
			self.assertTrue(exists)
