"""Test for the Ingredients API"""
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='test@example.com', password='Password'):
	"""Create and return a new user"""
	return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id: Ingredient.id):
	"""
	It takes an ingredient id and returns the url for the detail page of that ingredient

	:param ingredient_id: Ingredient.id
	:return: The url for the ingredient detail page.
	"""

	return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsAPITest(TestCase):
	"""Test unauthenticated API Requests"""

	def setUp(self):
		"""Set up of Tests"""
		self.client = APIClient()

	def test_auth_required(self):
		"""Test auth is required for retrieving Ingredients"""
		response = self.client.get(INGREDIENTS_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
	"""Test authenticated API Requests"""

	def setUp(self):
		"""Set up of Tests"""
		self.user = create_user()
		self.client = APIClient()
		self.client.force_authenticate(self.user)

	def test_retrieve_ingredients(self):
		"""Test retrieving a list of ingredients"""
		Ingredient.objects.create(user=self.user, name='Kale')
		Ingredient.objects.create(user=self.user, name='Vanilla')

		response = self.client.get(INGREDIENTS_URL)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		ingredients = Ingredient.objects.all().order_by('-name')
		serializer = IngredientSerializer(ingredients, many=True)

		self.assertEqual(response.data, serializer.data)

	def test_ingredients_limited_to_user(self):
		"""Test list of ingredients limited to user"""

		user2 = create_user(email='user2@example.com')
		Ingredient.objects.create(user=user2, name='Pork')
		ingredient = Ingredient.objects.create(user=self.user, name='Tomato')

		response = self.client.get(INGREDIENTS_URL)

		self.assertEqual(status.HTTP_200_OK, response.status_code)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0].get('name'), ingredient.name)
		self.assertEqual(response.data[0].get('id'), ingredient.id)

	def test_update_ingredient(self):
		"""
		We create an ingredient, then we make a patch request to the detail url of that ingredient, with a new name.
		assert that the response is 200 OK and that the ingredient's name has been updated
		"""
		ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
		payload = {
			'name': 'Coriander'
		}
		url = detail_url(ingredient.id)
		response = self.client.patch(url, payload)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ingredient.refresh_from_db()
		self.assertEqual(ingredient.name, payload.get('name'))

	def test_delete_recipe(self):
		"""
		Test Delete Ingredient
		we create an ingredient, then we delete it,
		then Checking that the response status code is 204 No Content, and that the ingredient no longer exists.
		"""
		ingredient = Ingredient.objects.create(user=self.user, name='Cinnamon')
		url = detail_url(ingredient.id)
		response = self.client.delete(url)

		ingredient = Ingredient.objects.filter(user=self.user)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(ingredient.exists())
