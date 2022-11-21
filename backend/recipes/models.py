from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


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
        Tags,
        related_name='recipes',
        verbose_name='Тэги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиены рецепта'
    )

    def __str__(self):
        return f'"{self.name}" (c){self.author}'


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
