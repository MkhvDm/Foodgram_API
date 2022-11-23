from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX'
        # add Hex validator
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Короткое имя'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Картинка'
    )
    cooking_time = models.IntegerField(
        blank=False,
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления - 1 минута.')
        ],
        verbose_name='Время приготовления, мин'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиены рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'"{self.name}" (c){self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        # related_name ???
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
        # related_name ???
    )
    amount = models.IntegerField(
        blank=False,
        validators=[
            MinValueValidator(1, 'Минимальное количество - 1.')
        ],
    )

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'

    def __str__(self):
        return f'{self.recipe}: {self.amount} of {self.ingredient}'


class UserRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт для пользователя'
        verbose_name_plural = 'Рецепты для пользователя'


class FavoriteRecipes(UserRecipes):

    def __str__(self):
        return f'{self.user} like {self.recipe}'

    class Meta:
        verbose_name = 'Избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователя'


class ShopList(UserRecipes):

    def __str__(self):
        return f'{self.user} will cook {self.recipe}'

    class Meta:
        verbose_name = 'Рецепт для списка покупок пользователя'
        verbose_name_plural = 'Рецепты для списка покупок пользователя'
