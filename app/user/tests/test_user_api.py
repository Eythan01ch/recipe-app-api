"""
tests for the user api
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
	"""helper function for creating a new user"""
	return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
	"""Test the Public Features of the user API"""

	def setUp(self):
		"""
			creating the client
		"""
		self.client = APIClient()

	def test_create_user_success(self):
		"""test creating a user is successful"""

		payload = {
			'email':    'test@example.com',
			'password': 'password123',
			'name':     'Test Name'
		}

		response = self.client.post(CREATE_USER_URL, payload)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		user = get_user_model().objects.get(email=payload.get('email'))
		self.assertTrue(user.check_password(payload.get('password')))
		self.assertNotIn('password', response.data)

	def test_user_with_email_exist_error(self):
		"""Test error returned if user with email exist"""

		payload = {
			'email':    'test@example.com',
			'password': 'password123',
			'name':     'Test Name'
		}
		create_user(**payload)
		response = self.client.post(CREATE_USER_URL, payload)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_password_too_short_error(self):
		"""test an error returned if password is too short"""

		payload = {
			'email':    'test@example.com',
			'password': 'pass',
			'name':     'Test Name'
		}
		response = self.client.post(CREATE_USER_URL, payload)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		user_exists = get_user_model().objects.filter(
			email=payload.get('email')
		).exists()

		self.assertFalse(user_exists)
