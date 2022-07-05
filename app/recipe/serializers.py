"""serializers for recipes API"""

from core.models import (Ingredient, Recipe, Tag)
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
	"""Serializer for Ingredients."""

	class Meta:
		"""Metadata for IngredientSerializer"""

		model = Ingredient
		fields = ['name', 'id']
		read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
	"""Serializer for tags."""

	class Meta:
		"""Metadata for TagSerializer"""

		model = Tag
		fields = ['name', 'id']
		read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
	"""serializer for Recipe"""
	tags = TagSerializer(many=True, required=False)

	class Meta:
		"""Metadata for RecipeSerializer"""
		model = Recipe
		fields = [
			'id',
			'title',
			'time_minutes',
			'price',
			'link',
			'tags',
			'ingredients',
		]
		read_only_fields = ['id']

	def _get_or_create_tags(self, tags, recipe):
		"""Handle getting or creating tags"""
		auth_user = self.context.get('request').user
		for tag in tags:
			tag_obj, created = Tag.objects.get_or_create(
				user=auth_user,
				**tag,
			)
			recipe.tags.add(tag_obj)

	def _get_or_create_ingredients(self, ingredients, recipe):
		"""Handle getting or creating ingredients"""
		auth_user = self.context.get('request').user
		for ingredient in ingredients:
			ingredient_obj, created = Ingredient.objects.get_or_create(
				user=auth_user,
				**ingredient,
			)
			recipe.ingredients.add(ingredient_obj)

	def create(self, validated_data):
		"""Create a Recipe"""
		tags = validated_data.pop('tags', [])
		ingredients = validated_data.pop('ingredients', ['lorem', 'ipsum'])
		recipe = Recipe.objects.create(**validated_data)
		self._get_or_create_tags(tags=tags, recipe=recipe)
		self._get_or_create_ingredients(ingredients=ingredients, recipe=recipe)
		return recipe

	def update(self, instance, validated_data):
		"""Update recipe"""
		tags = validated_data.pop('tags', None)
		ingredients = validated_data.pop('ingredients', None)

		if tags is not None:
			instance.tags.clear()
			self._get_or_create_tags(tags=tags, recipe=instance)

		if ingredients is not None:
			instance.ingredients.clear()
			self._get_or_create_ingredients(ingredients=ingredients, recipe=instance)

		for attr, value in validated_data.items():
			setattr(instance, attr, value)

		instance.save()
		return instance


class RecipeDetailSerializer(RecipeSerializer):
	"""serializer for Recipe detail View"""

	class Meta(RecipeSerializer.Meta):
		"""Metadata for RecipeDetailSerializer"""
		fields = RecipeSerializer.Meta.fields + ['description']
