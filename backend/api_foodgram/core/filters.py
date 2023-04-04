import django_filters
from recipes.models import Recipe


"""
class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        field_name='favorites'
        )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='shopping_cart'
        )
    author = django_filters.NumberFilter(
        field_name='author'
        )
    tags = django_filters.CharFilter(
        field_name='tags__slug', lookup_expr='exact'
        )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
"""