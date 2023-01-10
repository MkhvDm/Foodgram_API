from django_filters import rest_framework as filters
# import django_filters


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter('author__id')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

