"""
test for models
"""

from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import models


def create_user(email='user@example.com', password='password123'):
	"""Create and returns user"""
	return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
	"""Test Models."""

	def test_create_user_with_email_successful(self):
		"""
			made for testing test_create_user_with_email_successful
		"""
		email = 'test@example.com'
		password = 'testpass123'
		user = get_user_model().objects.create_user(
			email=email,
			password=password
		)

		self.assertEqual(user.email, email)
		self.assertTrue(user.check_password(password))

	def test_new_user_email_normalized(self):
		"""
		test email is normalized for new users
		"""
		sample_emails = [
			['test1@EXAMPLE.com', 'test1@example.com'],
			['Test2@Example.com', 'Test2@example.com'],
			['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
			['test4@example.COM', 'test4@example.com'],
		]

		for email, expected in sample_emails:
			user = get_user_model().objects.create_user(email=email, password='123')
			self.assertEqual(user.email, expected)

	def test_new_user_without_email_raises_error(self):
		"""Test that creating user without email will raise an error"""

		with self.assertRaises(ValueError):
			get_user_model().objects.create_user('', 'password123')

	def test_create_superuser(self):
		"""Test Creating a superuser"""
		user = get_user_model().objects.create_superuser(
			'test@example.com',
			'password123',
		)
		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_staff)

	def test_create_recipe(self):
		"""test creat recipe is successful"""

		user = get_user_model().objects.create_user(
			'test@example.com',
			'password123'
		)
		recipe = models.Recipe.objects.create(
			user=user,
			title='Sample Recipe Name',
			time_minutes=5,
			price=Decimal("5.50"),
			description='Sample Recipe Description'
		)
		self.assertEqual(str(recipe), recipe.title)

	def test_create_tag(self):
		"""Test Creating a tag is successful"""
		user = create_user()
		tag = models.Tag.objects.create(user=user, name='Tag1')

		self.assertEqual(str(tag), tag.name)

	def test_create_ingredient(self):
		"""Test creating an ingredient is successful"""
		user = create_user()
		ingredient = models.Ingredient.objects.create(
			user=user,
			name='Ingredient1'
		)
		self.assertEqual(str(ingredient), ingredient.name)

	@patch('core.models.uuid.uuid4')
	def test_recipe_file_name_uuid(self, mock_uuid):
		"""Test Generated image path"""
		uuid = 'test_uuid'
		mock_uuid.return_value = uuid
		file_path = models.recipe_image_file_path(None, 'example.jpg')
		self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')