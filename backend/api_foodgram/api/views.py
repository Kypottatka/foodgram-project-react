from datetime import datetime as dt

from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    DjangoModelPermissions,
)

from api.pagination import CustomPagination
from api.permissions import (
    AdminOrReadOnly,
    AuthorStaffOrReadOnly,
)
from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    OptimizedRecipeSerializer,
    TagSerializer,
    SubscriptionSerializer,
    UserSerializer
)
from core.enums import Tuples, UrlQueries
from recipes.models import ShoppingCart, Favorite, Ingredient, Recipe, Tag
from users.models import Subscriptions, CustomUser

from django.conf import settings


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomPagination
    permission_classes = (DjangoModelPermissions,)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        user = request.user
        subscription = Subscriptions.objects.filter(user=user, author=author)

        if request.method == 'POST' and not subscription:
            Subscriptions.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('get',),
        detail=False
    )
    def subscriptions(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            CustomUser.objects.filter(subscribers__user=request.user)
        )
        serializer = SubscriptionSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post',),
        detail=False,
        permission_classes=(AllowAny,)
    )
    def register(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
        queryset = self.queryset

        if name:
            name = name.lower()
            start_queryset = list(queryset.filter(name__istartswith=name))
            ingridients_set = set(start_queryset)
            cont_queryset = queryset.filter(name__icontains=name)
            start_queryset.extend(
                [ing for ing in cont_queryset if ing not in ingridients_set]
            )
            queryset = start_queryset

        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.apply_filters(self.queryset)

    def apply_filters(self, queryset):
        queryset = self.filter_by_tags(queryset)
        queryset = self.filter_by_author(queryset)
        queryset = self.filter_by_shop_cart(queryset)
        queryset = self.filter_by_favorite(queryset)
        return queryset

    def filter_by_tags(self, queryset):
        tags = self.request.query_params.getlist(UrlQueries.TAGS.value)
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()
        return queryset

    def filter_by_author(self, queryset):
        author = self.request.query_params.get(UrlQueries.AUTHOR.value)
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    def filter_by_shop_cart(self, queryset):
        if self.request.user.is_anonymous:
            return queryset

        shop_cart = self.request.query_params.get(UrlQueries.SHOP_CART)

        if shop_cart in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_carts__user=self.request.user)

        elif shop_cart in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        return queryset

    def filter_by_favorite(self, queryset):
        if self.request.user.is_anonymous:
            return queryset

        favorite = self.request.query_params.get(UrlQueries.FAVORITE)

        if favorite in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_favorites__user=self.request.user)

        elif favorite in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(self.queryset, id=pk)
        favorite = request.user.favorites.filter(recipe=recipe).first()

        if not favorite:
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = OptimizedRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(self.queryset, id=pk)
        shopping_cart = request.user.carts.filter(recipe=recipe).first()

        if not shopping_cart:
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = OptimizedRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        filename, shopping_list = self.generate_shopping_list(user)
        response = self.create_downloadable_response(filename, shopping_list)
        return response

    def generate_shopping_list(self, user):
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
            f'{dt.now().strftime(settings.DATE_TIME_FORMAT)}\n'
        ]

        ingredients = Ingredient.objects.filter(
            recipe__recipe__in_carts__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )

        shopping_list.append('\nПосчитано в Foodgram')
        shopping_list = '\n'.join(shopping_list)

        return filename, shopping_list

    def create_downloadable_response(self, filename, shopping_list):
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
