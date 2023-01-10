from django.contrib import admin, auth

from django.contrib.auth import get_user_model
from .models import (Ingredient, Tag, Recipe, RecipeIngredient,
                     FavoriteRecipe, ShopRecipe)

User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', )
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeIngredientInline,
    ]
    list_display = (
        'name',
        'author',
    )
    list_filter = ('author', 'name', 'tags', )
    search_fields = ('text', )
    # TODO: https://www.dothedev.com/blog/django-admin-show-custom-field-list_display/


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', )
    list_filter = ('recipe',)


@admin.register(FavoriteRecipe)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', )


@admin.register(ShopRecipe)
class ShopListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', )
