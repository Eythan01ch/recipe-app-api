"""Views For recipe API"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from . import serializers
from ..core.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
	"""View for manage Recipe APIs"""
	serializer = serializers.RecipeSerializer
	queryset = Recipe.objects.all()
	authentication_classes = [TokenAuthentication]
	permissions_classes = [IsAuthenticated]

	def get_queryset(self):
		"""retrieving recipes for the authenticated user"""
		return self.queryset.filter(user=self.request.user).order_by('-id')
