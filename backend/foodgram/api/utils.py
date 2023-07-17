from recipes.models import ShoppingList


def create_shopping_list_file(user):
    shopping_list = ShoppingList.objects.filter(user=user)
    ingredients = {}
    for item in shopping_list:
        for ingredient in item.recipe.ingredients.all():
            if hasattr(ingredient, 'amount'):
                if ingredient.name in ingredients:
                    ingredients[ingredient.name] += ingredient.amount
                else:
                    ingredients[ingredient.name] = ingredient.amount
            else:
                if hasattr(ingredient, 'ingredien'):
                    if ingredient.name in ingredients:
                        ingredients[ingredient.name] += ingredient.ingredien
                    else:
                        ingredients[ingredient.name] = ingredient.ingredien

    output = ''
    for name, amount in ingredients.items():
        output += f'{name} - {amount} {name.measurement_unit}\n'
    return output
