from django.urls import include, path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

# from .views import CustomUserCreateView, UserApiView
# from api.views import FollowViewSet
from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    subscriptions, subscribe)

router = DefaultRouter()
# router.register(r'users', FollowApiView, basename='follows')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('users/<int:id>/subscribe/', subscribe, name='subscribe'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
