"""serializers for recipes API"""

from rest_framework import serializers

from core.models import (Recipe, Tag)


class RecipeSerializer(serializers.ModelSerializer):
	"""serializer for Recipe"""

	class Meta:
		"""Metadata for RecipeSerializer"""
		model = Recipe
		fields = ['id', 'title', 'time_minutes', 'price', 'link']
		read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
	"""serializer for Recipe detail View"""

	class Meta(RecipeSerializer.Meta):
		"""Metadata for RecipeDetailSerializer"""
		fields = RecipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):
	"""Serializer for tags."""

	class Meta:
		model = Tag
		fields = ['name', 'id']
		read_only_fields = ['id']