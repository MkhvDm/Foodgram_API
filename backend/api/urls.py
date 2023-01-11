from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register(r'users', FollowViewSet, basename='follows')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
