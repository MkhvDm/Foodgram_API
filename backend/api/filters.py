from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter('author__id')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
