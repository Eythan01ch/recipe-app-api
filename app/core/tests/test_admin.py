"""
test for the django admin modification.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
	"""Tests for the Django admin"""

	def setUp(self):
		"""setting up client, user for tests"""
		self.client = Client()
		self.admin_user = get_user_model().objects.create_superuser(
			email='admin@example.com',
			password='password123',
		)
		self.client.force_login(self.admin_user)
		self.user = get_user_model().objects.create_user(
			email='user@example.com',
			password='password123',
			name='Test User',
		)

	def test_users_list(self):
		"""Test that users are listed on the page"""

		url = reverse('admin:core_user_changelist')
		response = self.client.get(url)

		self.assertContains(response, self.user.name)
		self.assertContains(response, self.user.email)

	def test_edit_user_page(self):
		"""Test The user edit page works """
		url = reverse('admin:core_user_change', args=[self.user.id])
		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)

	def test_create_user_page(self):
		"""Test Create user page works"""

		url = reverse('admin:core_user_add')

		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)
