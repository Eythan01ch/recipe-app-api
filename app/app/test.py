"""sample tests"""

from django.test import SimpleTestCase

from . import calc


class ClacTests(SimpleTestCase):

	def test_add(self):
		res = calc.add(5, 6)
		self.assertEqual(res, 11)

	def test_substract(self):
		res = calc.subtract(10, 15)

		self.assertEqual(res, 5)
