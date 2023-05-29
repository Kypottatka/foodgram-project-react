from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField,
    IntegerField, ReadOnlyField,
)

from core.services import recipe_ingredients_set
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class UserWithSubscriptionSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        user = self.context.get('view').request.user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()


class OptimizedRecipeSerializer(ModelSerializer):
    """
    Оптимизированная версия сериализатора для списка рецептов.
    """
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class AmountIngredientSerializer(ModelSerializer):
    id = IntegerField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserWithSubscriptionSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(
        many=True,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'name',
            'text',
            'image',
            'author',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user
        return recipe.in_favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        return recipe.in_carts.filter(user=user).exists()

    def validate(self, data):
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags_ids or not ingredients:
            raise ValidationError('Недостаточно данных.')

        exists_tags = Tag.objects.filter(id__in=tags_ids)
        if len(exists_tags) != len(tags_ids):
            raise ValidationError('Указан несуществующий тэг')
        valid_ings = {}
        for ing in ingredients:
            if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
                raise ValidationError('Неправильное количество ингидиента')

            amount = valid_ings.get(ing['id'], 0) + int(ing['amount'])
            valid_ings[ing['id']] = amount

        if not valid_ings:
            raise ValidationError('Неправильные ингидиенты')

        db_ings = Ingredient.objects.filter(pk__in=valid_ings.keys())

        if not db_ings:
            raise ValidationError('Неправильные ингидиенты')

        for ing in db_ings:
            valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

        data.update({
            'tags': tags_ids,
            'ingredients': valid_ings,
            'author': self.context.get('request').user
        })
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            AmountIngredient.objects.filter(recipe=recipe)
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe


class SubscriptionSerializer(UserWithSubscriptionSerializer):
    recipes = OptimizedRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()
