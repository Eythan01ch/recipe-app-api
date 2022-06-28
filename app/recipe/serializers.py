"""serializers for recipes API"""

from rest_framework import serializers

from app.core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
	"""serializer for Recipe"""

	class Meta:
		"""Metadata for RecipeSerializer"""
		model = Recipe
		fields = ['id', 'title', 'time_minutes', 'price', 'link']
		read_only_fields = ['id']
