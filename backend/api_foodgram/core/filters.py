from django.contrib.auth import get_user_model
from django_filters.rest_framework import CharFilter, FilterSet, filters

from recipes.models import Recipe, Tag, Ingredient

User = get_user_model()


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'author', 'tags', 'is_in_shopping_cart']

    def get_tags(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                tags__slug__in=value).distinct()
        return queryset

    def get_author(self, queryset, name, value):
        if value:
            queryset = queryset.filter(author=value)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset

        if value:
            queryset = queryset.filter(in_carts__user=self.request.user)

        else:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        return queryset

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset

        if value:
            queryset = queryset.filter(in_favorites__user=self.request.user)

        else:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset
