"""Views For recipe API"""

from core.models import (Recipe, Tag, Ingredient)
from recipe import serializers
from rest_framework import (mixins, viewsets, status)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
	extend_schema_view,
	extend_schema,
	OpenApiParameter,
	OpenApiTypes,
)


@extend_schema_view(
	list=extend_schema(
		parameters=[
			OpenApiParameter(
				'tags',
				OpenApiTypes.STR,
				description='Comma seperated list of IDs to FILTER',
			),
			OpenApiParameter(
				'ingredients',
				OpenApiTypes.STR,
				description='Comma seperated list of IDs to FILTER',
			)
		]
	)
)
class RecipeViewSet(viewsets.ModelViewSet):
	"""View for manage Recipe APIs"""
	serializer_class = serializers.RecipeDetailSerializer
	queryset = Recipe.objects.all()
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	@staticmethod
	def _params_to_inits(qs):
		"""convert str to int"""
		return [int(str_id) for str_id in qs.split(',')]

	def get_queryset(self):
		"""retrieving recipes for the authenticated user"""

		# We're getting the tags and ingredients from the query params.
		tags = self.request.query_params.get('tags')
		ingredients = self.request.query_params.get('ingredients')

		# It's just setting the queryset to the queryset that we're getting from the viewset.
		queryset = self.queryset

		# Filtering the queryset based on the tags that are passed in.
		if tags:
			tags_ids = self._params_to_inits(tags)
			queryset = queryset.filter(tags__id__in=tags_ids)

		# Filtering the queryset based on the ingredients that are passed in.
		if ingredients:
			ingredients_ids = self._params_to_inits(ingredients)
			queryset = queryset.filter(ingredients__id__in=ingredients_ids)

		# We're filtering the queryset by the user that is making the request, then we're ordering the queryset by the id,
		# and then we're making sure that we're only getting distinct results.
		return queryset.filter(user=self.request.user, ).order_by('-id').distinct()

	def get_serializer_class(self):
		"""overwrite the get serializer for getting the detail serializer when needed
		"""
		if self.action == 'list':
			return serializers.RecipeSerializer
		elif self.action == 'upload_image':
			return serializers.RecipeImageSerializer
		return self.serializer_class

	def perform_create(self, serializer):
		"""Create New Recipe"""
		serializer.save(user=self.request.user)

	@action(methods=['POST'], detail=True, url_path='upload_image')
	def upload_image(self, request, pk=None):
		"""
		We're getting the recipe object, then we're getting the serializer for that object, then we're passing in the request
		data to the serializer, then we're checking if the serializer is valid, then we're saving the serializer, then we're
		returning the serializer data with a 200 status code, and if the serializer is not valid, we're returning the
		serializer errors with a 400 status code

		:param request: The request object
		:param pk: The primary key of the recipe that we want to update
		:return: The serializer.data is being returned.
		"""
		recipe = self.get_object()
		serializer = self.get_serializer(recipe, data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
	list=extend_schema(
		parameters=[
			OpenApiParameter(
				'assigned_only',
				OpenApiTypes.INT,
				enum=[0, 1],
				description='Filter by items assigned to recipe',
			),
		]
	)
)
class BaseRecipeAttrViewSet(
	mixins.UpdateModelMixin,
	mixins.ListModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet
):
	"""Manage attrs of the recipe in the Database"""
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		"""retrieving ingredients for the authenticated user"""
		assigned_only = bool(
			int(self.request.query_params.get('assigned_only', 0))
		)

		queryset = self.queryset
		if assigned_only:
			queryset = queryset.filter(recipe__isnull=False)

		return queryset.filter(user=self.request.user).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
	"""Manage tags in the Database"""
	serializer_class = serializers.TagSerializer
	queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
	"""Manage ingredients in the Database"""
	serializer_class = serializers.IngredientSerializer
	queryset = Ingredient.objects.all()
