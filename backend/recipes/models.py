from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега для рецептов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX'
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
    """Модель ингредиента для рецептов."""
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единицы измерения'
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
        related_name='recipes',
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
        blank=False,
        related_name='recipes',
        verbose_name='Тэги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'"{self.name}" (c) {self.author}'


class RecipeIngredient(models.Model):
    """Модель, связывающая рецепт с ингредиентами и их количеством."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Игредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        blank=False,
        validators=[
            MinValueValidator(1, 'Минимальное количество - 1.')
        ],
    )

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='UQ_recipe_ingredient')
        ]

    def __str__(self):
        return f'{self.recipe}: {self.amount} of {self.ingredient}'


class UserRecipe(models.Model):
    """Абстрактная модель списка рецептов пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name="%(class)ss"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)ss'
        # todo related_name
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='UQ_user_recipe')
        ]
        verbose_name = 'Рецепт для пользователя'
        verbose_name_plural = 'Рецепты для пользователя'


class FavoriteRecipe(UserRecipe):
    """Модель избранного рецепта пользователя."""

    def __str__(self):
        return f'{self.user} like {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='UQ_favorite_user_recipe')
        ]
        verbose_name = 'Избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователя'


class ShopRecipe(UserRecipe):
    """Модель рецепта для списка покупок пользователя."""

    def __str__(self):
        return f'{self.user} will cook {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='UQ_shoplist_user_recipe')
        ]
        verbose_name = 'Рецепт для списка покупок пользователя'
        verbose_name_plural = 'Рецепты для списка покупок пользователя'
