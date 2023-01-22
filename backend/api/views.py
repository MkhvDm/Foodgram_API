import datetime

from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, ExpressionWrapper, Q, Sum
from django.http import FileResponse
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShopRecipe, Tag)

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAdmin, IsAuthor, ReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, ShortRecipes, TagSerializer,
                          UserWithRecipes)
from .utils import gen_pdf

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAdmin | IsAuthor | ReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('tags', )

    def get_queryset(self):
        recipes = Recipe.objects.all()
        user = self.request.user

        if user.is_authenticated:
            recipes = recipes.annotate(
                is_favorited=ExpressionWrapper(
                    Q(id__in=user.favoriterecipes.all().values('recipe')),
                    output_field=BooleanField()
                ),
                is_in_shopping_cart=ExpressionWrapper(
                    Q(id__in=user.shoprecipes.all().values('recipe')),
                    output_field=BooleanField()
                )
            )
        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', ):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def _user_recipes_controller(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        is_exists = model.objects.filter(user=user, recipe=recipe).exists()
        if request.method == 'POST':
            if is_exists:
                return Response(
                    {'errors': 'Рецепт уже в списке.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(recipe=recipe, user=request.user)
            serializer = ShortRecipes(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not is_exists:
            return Response(
                {'errors': 'Рецепт не в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_recipes = model.objects.filter(user=user, recipe=recipe)
        user_recipes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self._user_recipes_controller(request, pk, FavoriteRecipe)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self._user_recipes_controller(request, pk, ShopRecipe)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shop_recipes_ids = request.user.shoprecipes.all().values('recipe')
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe_id__in=shop_recipes_ids)
            .select_related('ingredient')
            .values('ingredient__name')
            .annotate(total=Sum('amount'))
            .values(
                'ingredient__name',
                'total',
                'ingredient__measurement_unit'
            )
        )

        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(
                f'{ingredient.get("ingredient__name").capitalize()} '
                f'({ingredient.get("ingredient__measurement_unit")}) — '
                f'{ingredient.get("total")}'
            )
        return FileResponse(
            gen_pdf(ingredients_list),
            as_attachment=True,
            filename=f'{request.user} shoplist {datetime.date.today()}.pdf'
        )


class TagViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )


class FollowViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        current_user = request.user
        followings = current_user.follows.values('author')
        followings_users = (
            User.objects.filter(id__in=followings)
                .annotate(recipes_count=Count('recipes__id'))
        )
        followings_users = self.paginate_queryset(followings_users)
        serializer = UserWithRecipes(
            followings_users, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        current_user = request.user
        resp = {}
        if author == current_user:
            resp['errors'] = 'Необходимо передать id другого пользователя.'
            response_status = status.HTTP_400_BAD_REQUEST
        else:
            is_following = current_user.follows.filter(author=author).exists()
            if request.method == 'POST':
                if is_following:
                    resp['errors'] = (
                        'Вы уже подписаны на данного пользователя.'
                    )
                    response_status = status.HTTP_400_BAD_REQUEST
                else:
                    current_user.follows.create(author=author)
                    user_with_num_recipes = (
                        User.objects.filter(pk=pk)
                        .annotate(recipes_count=Count('recipes__id'))
                    )
                    serializer = UserWithRecipes(
                        user_with_num_recipes[0], context={'request': request}
                    )
                    resp = serializer.data
                    response_status = status.HTTP_201_CREATED
            else:
                if not is_following:
                    resp['errors'] = 'Вы не подписаны на данного пользователя.'
                    response_status = status.HTTP_400_BAD_REQUEST
                else:
                    current_user.follows.filter(author=author).delete()
                    response_status = status.HTTP_204_NO_CONTENT
        return Response(resp, status=response_status)
