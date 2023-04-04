from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from django.db.models import F, Q, Sum

from .pagination import CustomPagination
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    UserReadSerializer,
    UserCreateSerializer,
    SetPasswordSerializer,
    SubscriptionsSerializer,
    SubscribeAuthorSerializer,
)
from .permissions import (
    AdminOrReadOnly,
    AuthorStaffOrReadOnly,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
)
from users.models import User, Subscribe


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self) -> list[Ingredient]:
        name: str = self.request.query_params.get('name')
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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = (AuthorStaffOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user,)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        if self.request.user.is_anonymous:
            return queryset

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart in ('1', 'true'):
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_cart in ('0', 'false'):
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorit = self.request.query_params.get('is_favorited')
        if is_favorit in ('1', 'true'):
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorit in ('0', 'false'):
            queryset = queryset.exclude(in_favorites__user=self.request.user)
        return queryset

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._add_del_obj(pk, Favorite, Q(recipe__id=pk))

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self._add_del_obj(pk, ShoppingCart, Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
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
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(
            detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,),
            url_path='me')
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data)

    @action(
            detail=False,
            methods=['post'],
            url_path='set_password',
            permission_classes=(IsAuthenticated,))
    def set_password(self, request, pk=None):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(
                    serializer.data['current_password']):
                return Response(
                    {'current_password': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            request.user.set_password(serializer.data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

    @action(
            detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscribeAuthorSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            get_object_or_404(
                Subscribe,
                user=request.user,
                author=author
            ).delete()
            return Response(
                {'detail': 'Успешная отписка'},
                status=status.HTTP_204_NO_CONTENT
            )
