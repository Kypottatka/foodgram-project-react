from django.shortcuts import get_object_or_404

from recipes.models import AmountIngredient, Ingredient


def recipe_ingredients_set(recipe, ingredients) -> None:
    recipe_ingredients = list()
    for ing_id, ing_amount in ingredients.items():
        recipe_ingredients.append(
            AmountIngredient(
                ingredient=get_object_or_404(Ingredient, id=ing_id),
                recipe=recipe,
                amount=ing_amount[1],
            )
        )
    AmountIngredient.objects.bulk_create(recipe_ingredients)
