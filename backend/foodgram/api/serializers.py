from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Subscribed
from recipes.models import (Tag, Ingredient, Recipe, IngredientRecipe,
                            ShoppingList, Favorite)


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscribed.objects.filter(user=user, author=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribed
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
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get_or_create(**ingredient_data)[0]
            amount = ingredient_data['amount']
            IngredientRecipe.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        ingredient_mapping = {
            ingredient.id: ingredient
            for ingredient in instance.ingredients.all()
            }
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id', None)
            if ingredient_id:
                ingredient = ingredient_mapping.pop(ingredient_id)
                ingredient.name = ingredient_data.get('name', ingredient.name)
                ingredient.measurement_unit = ingredient_data.get(
                    'measurement_unit', ingredient.measurement_unit)
                ingredient.save()
            else:
                ingredient = Ingredient.objects.create(**ingredient_data)
            amount = ingredient_data['amount']
            IngredientRecipe.objects.update_or_create(
                                                    recipe=recipe,
                                                    ingredient=ingredient,
                                                    defaults={'amount': amount}
            )
        for ingredient in ingredient_mapping.values():
            ingredient.delete()
        return recipe

