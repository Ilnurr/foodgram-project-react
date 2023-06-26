from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction

from users.models import User, Subscriber
from recipes.models import (Tag, Ingredient, Recipe, IngredientRecipe,
                            ShoppingList, Favorite)


class UsersSerializer(UserSerializer):
    is_Subscriber = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password', 'is_Subscriber')

    def get_is_Subscriber(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscriber.objects.filter(user=user, author=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ('id', 'user', 'author')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount')


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = UsersSerializer()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = '__all__'


@transaction.atomic()
def create_recipe(validated_data):
    ingredients_data = validated_data.pop('ingredients')
    recipe = Recipe.objects.create(**validated_data)
    ingredient_objs = []
    for ingredient_data in ingredients_data:
        ingredient, created = Ingredient.objects.get_or_create(
            **ingredient_data)
        amount = ingredient_data['amount']
        ingredient_objs.append(IngredientRecipe(recipe=recipe,
                                                ingredient=ingredient,
                                                amount=amount))
        IngredientRecipe.objects.bulk_create(ingredient_objs)
    return recipe


@transaction.atomic()
def update_recipe(instance, validated_data):
    ingredients_data = validated_data.pop('ingredients')
    recipe = instance
    ingredient_mapping = {
        ingredient.id: ingredient
        for ingredient in instance.ingredients.all()
    }
    ingredient_objs = []
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data.get('id', None)
    if ingredient_id:
        ingredient = ingredient_mapping.pop(ingredient_id)
        ingredient.name = ingredient_data.get('name', ingredient.name)
        ingredient.measurement_unit = ingredient_data.get(
            'measurement_unit',
            ingredient.measurement_unit)
        ingredient.save()
    else:
        ingredient = Ingredient.objects.create(**ingredient_data)
        amount = ingredient_data['amount']
        ingredient_objs.append(IngredientRecipe(
            recipe=recipe,
            ingredient=ingredient,
            amount=amount))
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        IngredientRecipe.objects.bulk_create(ingredient_objs)
    for ingredient in ingredient_mapping.values():
        ingredient.delete()
    return recipe
