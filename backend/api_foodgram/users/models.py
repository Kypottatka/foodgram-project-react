from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import (CASCADE, CharField, CheckConstraint,
                              DateTimeField, EmailField, F, ForeignKey, Model,
                              Q, UniqueConstraint)
from django.db.models.functions import Length

from core.validators import UserFieldsValidator

CharField.register_lookup(Length)


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        email,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email,
            username,
            first_name,
            last_name,
            password,
            **extra_fields
        )


class User(AbstractUser):
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.MAX_LEN_EMAIL_FIELD,
        unique=True,
    )
    username = CharField(
        verbose_name='Уникальный юзернейм',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        unique=True,
        validators=(
            UserFieldsValidator(field='username'),
        ),
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        validators=(UserFieldsValidator(
            regex='[^а-яёА-ЯЁ]+|[^a-zA-Z]+',
            field='Имя'),
        ),
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        validators=(UserFieldsValidator(
            regex='[^а-яёА-ЯЁ]+|[^a-zA-Z]+',
            field='Фамилия'),
        ),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscriptions(Model):
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscribers',
        to=User,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Подписчики',
        related_name='subscriptions',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='\nRepeat subscription\n',
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='\nNo self sibscription\n'
            )
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
