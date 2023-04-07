from recipes.models import (
    AmountIngredient,
    Recipe,
    Ingredient,
)


def recipe_ingredients_set(
    recipe: Recipe,
    ingredients: dict[int, tuple['Ingredient', int]]
) -> None:
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(AmountIngredient(
            recipe=recipe,
            ingredients=ingredient,
            amount=amount
        ))

    AmountIngredient.objects.bulk_create(objs)
