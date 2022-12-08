from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, get_object_or_404

from rest_framework.mixins import (ListModelMixin, CreateModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import Recipe, Tag, Ingredient
from users.models import Follow

# from .serializers import FollowSerializer
from .permissions import ReadOnly, IsAuthor, IsAdmin
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          FollowSerializer, UserWithRecipes)


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


@api_view(['GET'])  # TODO GENERIC VIEW OR VIEWSET (for pagination)
@permission_classes([IsAuthenticated])
def subscriptions(request):
    current_user = request.user
    followings = current_user.follows.values('author')
    followings_users = User.objects.filter(id__in=followings)

    print(followings_users.query)
    print(followings_users)
    print(type(followings_users))
    serializer = UserWithRecipes(followings_users, many=True)
    print(serializer.data)
    # TODO
    print(f'----- api_view -----')
    return Response(serializer.data)


class FollowViewSet(GenericViewSet):
    # TODO CHECK
    pass













@api_view(['POST', "DELETE"])
@permission_classes([IsAuthenticated])
def subscribe(request, user_id):
    author = get_object_or_404(User, pk=user_id)
    current_user = request.user
    response = {}
    if author == current_user:
        response['errors'] = 'Необходимо передать id другого пользователя.'
        response_status = status.HTTP_400_BAD_REQUEST
    else:
        is_following = current_user.follows.filter(author=author).exists()
        if request.method == 'POST':
            if is_following:
                response['errors'] = 'Вы уже подписаны на данного пользователя.'
                response_status = status.HTTP_400_BAD_REQUEST
            else:
                current_user.follows.create(author=author)
                limit = request.query_params.get('recipes_limit')  # TODO in serializer
                print(f'limit: {limit}')
                # recipes =
                serializer = UserWithRecipes(author)
                response = serializer.data
                print(response)  # TODO
                # response['result'] = 'follows done'
                response_status = status.HTTP_201_CREATED
        else:
            if not is_following:
                response['errors'] = 'Вы не подписаны на данного пользователя.'
                response_status = status.HTTP_400_BAD_REQUEST
            else:
                current_user.follows.filter(author=author).delete()
                response_status = status.HTTP_204_NO_CONTENT

    return Response(response, status=response_status)


# class FollowApiView(APIView):
#     """Подписки на авторов."""
#     authentication_classes = [AllowAny, ]
#     permission_classes = [IsAuthenticated, ]
#
#     @action(methods=['get'], detail=False, url_path=r'subscribe')
#     def subscribe(self, request):
#         return Response({'pk_arg': 'test'}, status=200)


    # serializer_class = FollowSerializer
    # permission_classes = (IsAuthenticated, )
    # filter_backends = (SearchFilter, )
    # search_fields = ('follower__username', 'author__username', )
    #
    # def get_queryset(self):
    #     user = self.request.user
    #     new_queryset = user.follows.all()
    #     return new_queryset
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
