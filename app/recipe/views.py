"""Views For recipe API"""

from core.models import (Recipe, Tag)
from recipe import serializers
from rest_framework import (mixins, viewsets)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
	"""View for manage Recipe APIs"""
	serializer_class = serializers.RecipeDetailSerializer
	queryset = Recipe.objects.all()
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		"""retrieving recipes for the authenticated user"""
		return self.queryset.filter(user=self.request.user).order_by('-id')

	def get_serializer_class(self):
		"""overwrite the get serializer for getting the detail serializer when needed
		"""
		if self.action == 'list':
			return serializers.RecipeSerializer
		return self.serializer_class

	def perform_create(self, serializer):
		"""Create New Recipe"""
		serializer.save(user=self.request.user)


class TagViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
	"""Manage tags in the Database"""

	serializer_class = serializers.TagSerializer
	queryset = Tag.objects.all()
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		"""retrieving tags for the authenticated user"""
		return self.queryset.filter(user=self.request.user).order_by('-name')
