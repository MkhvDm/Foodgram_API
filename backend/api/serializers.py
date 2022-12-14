from rest_framework import serializers
from django.contrib.auth import get_user_model
# from djoser.serializers import UserSerializer
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from users.models import Follow
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

from drf_extra_fields.fields import Base64ImageField


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ExtUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return False  # TODO is_subscribed


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = ExtUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart', )

    def get_is_favorited(self, obj):
        return False  # TODO is_favorited

    def get_is_in_shopping_cart(self, obj):
        return False  # TODO is_in_shopping_cart


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate(self, attrs):
        errors = {}
        for field in self.Meta.fields:
            # print(f'-- {field}')
            if field not in attrs:
                errors[field] = f'Необходимо заполнить поле {field}.'
            elif not attrs.get(field):
                errors[field] = f'Необходимо заполнить поле {field}.'
        if errors:
            raise ValidationError(errors)
        return attrs


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(
        many=True, write_only=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'image', 'text',
                  'cooking_time')

    def to_representation(self, instance):
        ingredients_amount = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True
        )
        tags = TagSerializer(instance.tags.all(), many=True)
        ret = super().to_representation(instance)
        ret['ingredients'] = ingredients_amount.data
        ret['tags'] = tags.data
        return ret

    def create(self, validated_data):
        # print(f'valid: {validated_data}')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        list_to_create = []
        for ingredient in ingredients:
            list_to_create.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        RecipeIngredient.objects.bulk_create(list_to_create)
        return recipe

    def validate(self, attrs):
        # print(f'ATTRS: {attrs}')
        errors = {}
        for field in self.Meta.fields:
            # print(f'-- {field}')
            if field not in attrs:
                errors[field] = f'Необходимо заполнить поле {field}.'
            elif not attrs.get(field):
                errors[field] = f'Необходимо заполнить поле {field}.'
        if errors:
            raise ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        print(f'validated_data: {validated_data}')
        ingredients = instance.recipe_ingredients.all()
        ingredients.delete()
        new_ingredients = validated_data.pop('ingredients')
        list_to_create = []
        for ingredient in new_ingredients:
            list_to_create.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        RecipeIngredient.objects.bulk_create(list_to_create)

        instance.tags.set(validated_data.pop('tags'))
        instance.image.delete(save=False)
        instance.image = validated_data.pop('image')
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance


# class ExtUserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['email', 'id', 'username', 'first_name', 'last_name',
#                   'is_subscribed']
#
#     def get_is_subscribed(self, obj):
#         return False  # TODO is_subscribed


class ShortRecipes(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipes(ExtUserSerializer):
    recipes = serializers.SerializerMethodField()
    # recipes = ShortRecipes(many=True)

    class Meta(ExtUserSerializer.Meta):
        fields = ExtUserSerializer.Meta.fields + ('recipes', )

    def get_recipes(self, obj):
        print('================')
        # get query param recipes_limit
        print(self)
        return {'1': 1, '2': 2, '3': 3}


class FollowSerializer(serializers.ModelSerializer):
    results = ExtUserSerializer(source='author')

    class Meta:
        model = Follow
        fields = ('results', )
        depth = 1


    # user = SlugRelatedField(
    #     slug_field='username',
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )
    #
    # following = SlugRelatedField(
    #     slug_field='username',
    #     read_only=False,
    #     queryset=User.objects.all()
    # )
    #
    # class Meta:
    #     model = Follow
    #     fields = ('user', 'following', )
    #     validators = [
    #         UniqueTogetherValidator(
    #             queryset=Follow.objects.all(),
    #             fields=('user', 'following', ),
    #             message='Вы уже подписаны на этого пользователя!'
    #         )
    #     ]
    #
    # def validate_following(self, value):
    #     """Rejects self-following."""
    #     user = self.context.get('request').user
    #     if value == user:
    #         raise serializers.ValidationError('Нельзя подписать на себя!')
    #     return value
