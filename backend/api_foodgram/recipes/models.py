from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    CheckConstraint,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    Q,
    TextField,
    UniqueConstraint
)
from django.db.models.functions import Length

from PIL import Image

from core.enums import Tuples
from users.models import User
from django.conf import settings

CharField.register_lookup(Length)


class Tag(Model):
    name = CharField(
        verbose_name='Тэг',
        max_length=settings.MAX_LEN_TAGS_CHARFIELD,
        unique=True,
    )
    color = CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
        db_index=False,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]
    )
    slug = CharField(
        verbose_name='Слаг тэга',
        max_length=64,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(Model):
    name = CharField(
        verbose_name='Ингридиент',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
    )
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=24,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient'
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(Model):
    name = CharField(
        verbose_name='Название блюда',
        max_length=settings.MAX_LEN_RECIPES_CHARFIELD,
    )
    author = ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        verbose_name='Тег',
        related_name='recipes',
        to='Tag',
    )
    ingredients = ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        through='AmountIngredient',
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/',
    )
    text = TextField(
        verbose_name='Описание блюда',
        max_length=settings.MAX_LEN_RECIPES_TEXTFIELD,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                'Ваше блюдо уже готово!',
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME,
                'Очень долго ждать...',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image = image.resize(Tuples.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)


class AmountIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='+',
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGREDIENTS,
                'Нужно хоть какое-то количество.',
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT_INGREDIENTS,
                'Слишком много!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredients}'


class Favorite(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='Понравившиеся рецепты',
        related_name='in_favorites',
        on_delete=CASCADE,
    )
    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='in_carts',
        on_delete=CASCADE,
    )
    user = ForeignKey(
        User,
        verbose_name='Владелец списка',
        related_name='carts',
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
