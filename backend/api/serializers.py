from rest_framework import serializers
from django.contrib.auth import get_user_model
# from djoser.serializers import UserSerializer
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


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


class AmountIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.PrimaryKeyRelatedField(
        queryset=RecipeIngredient.objects.all(), #filter(recipe_id=recipe_id),
        many=True#,
        # read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = ExtUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    # ingredients = IngredientSerializer(many=True, read_only=True)
    ingredients = AmountIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'name', 'text', 'cooking_time',
                  'ingredients']





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
