from django.contrib.auth import get_user_model
from django.db.models import (Count, Prefetch, ExpressionWrapper, Q,
                              BooleanField, Sum)
from django.http import FileResponse
from rest_framework import status
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.generics import CreateAPIView, get_object_or_404
from django.core.exceptions import PermissionDenied

from rest_framework.mixins import (ListModelMixin, CreateModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (Recipe, Tag, Ingredient, FavoriteRecipe,
                            ShopRecipe, RecipeIngredient)
from users.models import Follow

# from .serializers import FollowSerializer
from .filters import RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import ReadOnly, IsAuthor, IsAdmin
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          FollowSerializer, UserWithRecipes, ShortRecipes)

from djoser.views import UserViewSet

from .utils import gen_pdf

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAdmin | IsAuthor | ReadOnly]
    # pagination_class = None  # FIXME TEMP
    filterset_class = RecipeFilter
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('tags', )

    def get_queryset(self):
        recipes = Recipe.objects.all()
        user = self.request.user
        filters = []
        print(f'QUERY PARAMS: {self.request.query_params}')
        is_fav_filter = self.request.query_params.get('is_favorited')
        print(f'Query: is fav? - {is_fav_filter}')
        is_shop_filter = self.request.query_params.get('is_in_shopping_cart')
        print(f'Query: is shop? - {is_shop_filter}')

        if is_fav_filter == '1':
            if not user.is_authenticated:
                raise PermissionDenied()
            favs_q = Q(id__in=FavoriteRecipe.objects.filter(user=user).values('recipe'))
            filters.append(favs_q)
            # fav_ids = FavoriteRecipe.objects.filter(user=self.request.user).values('recipe')
            # print(f'fav ids: {fav_ids}')
            # fav_recipes = Recipe.objects.filter(id__in=fav_ids)
            # print(f'fav recipes: {fav_recipes}')
            # return fav_recipes
        if is_shop_filter == '1':
            if not user.is_authenticated:
                raise PermissionDenied()
            print(f'Is shoping cart? - {is_shop_filter}')
            shop_q = Q(id__in=ShopRecipe.objects.filter(user=user).values('recipe'))
            filters.append(shop_q)
            # shop_ids = ShopRecipe.objects.filter(user=self.request.user).values('recipe')
            # shop_recipes = Recipe.objects.filter(id__in=shop_ids)
            # return shop_recipes

        if filters:
            recipes = recipes.filter(*filters)

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
        print(f'RESULT QS: {recipes}')
        # print(recipes.query)
        return recipes


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', ):
            return RecipeCreateSerializer
        return RecipeSerializer

    def _user_recipes_controller(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        is_exists = model.objects.filter(user=user, recipe=recipe).exists()
        print(f'IS EXIST? {is_exists} ({model})')
        if request.method == 'POST':
            if is_exists:
                return Response(
                    {'errors': 'Рецепт уже в списке.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(recipe=recipe, user=request.user)
            serializer = ShortRecipes(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not is_exists:
                return Response(
                    {'errors': 'Рецепт не в списке.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = model.objects.filter(user=user, recipe=recipe)  #todo rename user_list
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self._user_recipes_controller(request, pk, FavoriteRecipe)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self._user_recipes_controller(request, pk, ShopRecipe)

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny]) #IsAuthenticated
    def download_shopping_cart(self, request):
        request.user = User.objects.get(pk=1)
        shop_recipes_ids = request.user.shoprecipes.all().values('recipe')
        print(f'IDs: {shop_recipes_ids}')
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe_id__in=shop_recipes_ids)
            .select_related('ingredient')
            .values('ingredient__name')
            .annotate(total=Sum('amount'))
            .values('ingredient__name', 'total', 'ingredient__measurement_unit')
        )

        print(ingredients)
        ingredients_list = []
        for ingr in ingredients:
            ingredients_list.append(
                f'{ingr.get("ingredient__name").capitalize()} '
                f'({ingr.get("ingredient__measurement_unit")}) — '
                f'{ingr.get("total")}'
            )
        return FileResponse(gen_pdf(ingredients_list), as_attachment=True, filename='hello.pdf')


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
    filter_backends = (SearchFilter, )
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
