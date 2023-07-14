from recipes.models import IngredientRecipe, ShoppingList


def create_shopping_list_file(user):
    shopping_list = ShoppingList.objects.filter(user=user)
    ingredients = IngredientRecipe
    for item in shopping_list:
        for ingredient in item.recipe.ingredients.all():
            if ingredient.name in ingredients:
                ingredients[ingredient.name] += ingredient.amount
            else:
                ingredients[ingredient.name] = ingredient.amount
    output = ''
    for name, amount in ingredients.items():
        output += f'{name} - {amount} {ingredient.measurement_unit}\n'
    return output