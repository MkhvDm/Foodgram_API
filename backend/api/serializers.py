from rest_framework import serializers
from django.contrib.auth import get_user_model
# from djoser.serializers import UserSerializer
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

from drf_extra_fields.fields import Base64ImageField


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]
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
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

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
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def create(self, validated_data):
        print('Entry RecipeIngredientSerializer:')
        print(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    author = ExtUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    # image = CustomImageField()
    image = Base64ImageField()
    # image = CustomImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time']
        read_only_fields = ['id', 'author', 'is_favorited',
                            'is_in_shopping_cart', ]

    def get_is_favorited(self, obj):
        return False  # TODO is_favorited

    def get_is_in_shopping_cart(self, obj):
        return False  # TODO is_in_shopping_cart

    def validate(self, attrs):
        print('ATTRS:')
        print(attrs)

    def create(self, validated_data):
        print(validated_data)


class AddIngredientSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(read_only=True,
    #                                         source='ingredient')
    # id = serializers.IntegerField()
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    id = serializers.IntegerField(source='ingredient_id')
    # amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    # def validate(self, data):
    #     print(f'data: {data}')
    #     print(self.data)
    #     print(self.context)
    #     print(self.context.get('request'))
    #     # return validated_data = ....
    #
    # def create(self, validated_data):
    #     pass


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    # tags = AddTagsSerializer(many=True)
    # image =

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'name', 'image', 'text',
                  'cooking_time']
        # fields = '__all__'

    # def validate(self, attrs):
    #     print(f'attrs: {attrs}')

    def create(self, validated_data):
        print(f'RAW: {self.initial_data}')
        print(f'DATA: {validated_data}')
        ingredients = validated_data.pop('ingredients')
        print(f'INGR: {ingredients}')
        tags = validated_data.pop('tags')
        print(f'TAGS: {tags}')
        # create recipe
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # current_achievement, status = (
            #     RecipeIngredient.objects.get_or_create(**achievement)
            # )
        # add ingr, tags
        # return recipe
        print(f'Recipe create: {validated_data}')






# class UserWithRecipes(ExtUserSerializer):
#     recipes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta(ExtUserSerializer.Meta):
#         super().fields += 'recipes'


# class FollowSerializer(serializers.ModelSerializer):
#     user = SlugRelatedField(
#         slug_field='username',
#         read_only=True,
#         default=serializers.CurrentUserDefault()
#     )
#
#     following = SlugRelatedField(
#         slug_field='username',
#         read_only=False,
#         queryset=User.objects.all()
#     )
#
#     class Meta:
#         model = Follow
#         fields = ('user', 'following', )
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'following', ),
#                 message='Вы уже подписаны на этого пользователя!'
#             )
#         ]
#
#     def validate_following(self, value):
#         """Rejects self-following."""
#         user = self.context.get('request').user
#         if value == user:
#             raise serializers.ValidationError('Нельзя подписать на себя!')
#         return value
