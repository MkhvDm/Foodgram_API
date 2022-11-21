from django.contrib.auth import get_user_model
from rest_framework import SearchFilter
from rest_framework.generics import CreateAPIView, get_object_or_404

from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import FollowSerializer

User = get_user_model()


class FollowViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """Подписки на авторов."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    # filter_backends = (SearchFilter, )
    # search_fields = ('follower__username', 'author__username', )

    # def get_queryset(self):
    #     user = self.request.user
    #     new_queryset = user.follows.all()
    #     return new_queryset
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
