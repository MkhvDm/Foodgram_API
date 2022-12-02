from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, get_object_or_404

from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, Tag, Ingredient

# from .serializers import FollowSerializer
from .permissions import ReadOnly, IsAuthor, IsAdmin
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer, RecipeCreateSerializer)

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAdmin | IsAuthor | ReadOnly]
    pagination_class = None  # FIXME TEMP

    # TODO: get_queryset(): ...

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', ):
            return RecipeCreateSerializer
        return RecipeSerializer


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



# class FollowViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
#     """Подписки на авторов."""
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated, )
    # filter_backends = (SearchFilter, )
    # search_fields = ('follower__username', 'author__username', )

    # def get_queryset(self):
    #     user = self.request.user
    #     new_queryset = user.follows.all()
    #     return new_queryset
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
