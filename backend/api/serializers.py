from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }


class ExtUserSerializer(serializers.ModelSerializer):
    """Сериализатор отображения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.follows.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор количества игредиента длдя рецепта."""
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""
    author = ExtUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart', )


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента к рецепту."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate(self, attrs):
        errors = {}
        for field in self.Meta.fields:
            if field not in attrs:
                errors[field] = f'Необходимо заполнить поле {field}.'
            elif not attrs.get(field):
                errors[field] = f'Необходимо заполнить поле {field}.'
        if errors:
            raise ValidationError(errors)
        return attrs


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и редактирования рецепта."""
    ingredients = AddIngredientSerializer(
        many=True, write_only=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'name', 'image', 'text',
                  'cooking_time']
        read_only_fields = ['id']

    def to_representation(self, instance):
        ingredients_amount = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True
        )
        tags = TagSerializer(instance.tags.all(), many=True)
        ret = super().to_representation(instance)
        ret['id'] = instance.id
        ret['ingredients'] = ingredients_amount.data
        ret['tags'] = tags.data
        ret['author'] = ExtUserSerializer(
            instance.author,
            context={'request': super().context['request']}
        ).data
        ret['is_favorited'] = False
        ret['is_in_shopping_cart'] = False
        return ret

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        list_to_create, list_to_check = [], []
        for ingredient in ingredients:
            list_to_check.append(ingredient.get('id'))
            list_to_create.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        if len(set(list_to_check)) != len(ingredients):
            recipe.delete()
            raise ValidationError(
                detail={'ingredients': 'Ингредиенты дублируются!'}
            )
        RecipeIngredient.objects.bulk_create(list_to_create)
        return recipe

    def validate(self, attrs):
        errors = {}
        for field in self.Meta.fields:
            if field not in attrs:
                errors[field] = f'Необходимо заполнить поле {field}.'
            elif not attrs.get(field):
                errors[field] = f'Необходимо заполнить поле {field}.'
        if errors:
            raise ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        ingredients = instance.recipe_ingredients.all()
        new_ingredients = validated_data.pop('ingredients')
        list_to_create, list_to_check = [], []
        for ingredient in new_ingredients:
            list_to_check.append(ingredient.get('id'))
            list_to_create.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        if len(set(list_to_check)) != len(ingredients):
            raise ValidationError(
                detail={'ingredients': 'Ингредиенты дублируются!'}
            )
        ingredients.delete()
        RecipeIngredient.objects.bulk_create(list_to_create)

        instance.tags.set(validated_data.pop('tags'))
        instance.image.delete(save=False)
        instance.image = validated_data.pop('image')
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance


class ShortRecipes(serializers.ModelSerializer):
    """Сериализатор короткого отображения рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipes(ExtUserSerializer):
    """Сериализатор пользователя с рецептами."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta(ExtUserSerializer.Meta):
        fields = ExtUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context["request"]
        lim = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()[:int(lim)] if lim else obj.recipes.all()
        return ShortRecipes(
            recipes, many=True, context={"request": request}
        ).data
