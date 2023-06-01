import os
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='string_from_.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*',
    cast=Csv()
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost, http://127.0.0.1',
    cast=Csv(),
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api_foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_foodgram.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('ENGINE',
                            default='django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}

AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', # noqa
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
    ['rest_framework.authentication.TokenAuthentication', ],

    'DEFAULT_PERMISSION_CLASSES':
    ['rest_framework.permissions.IsAuthenticatedOrReadOnly', ],
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'recipe': ('api.permissions.AuthorStaffOrReadOnly,',),
        'recipe_list': ('api.permissions.AuthorStaffOrReadOnly',),
        'user': ('api.permissions.OwnerUserOrReadOnly',),
        'user_list': ('api.permissions.OwnerUserOrReadOnly',),
    },
    'SERIALIZERS': {
        'user_list': 'api.serializers.UserWithSubscriptionSerializer',
        'current_user': 'api.serializers.UserWithSubscriptionSerializer',
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_ADMIN = 'admin@example.com'

# Important project variables:

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'

PAGE_NUMBER = 6

MAX_LEN_EMAIL_FIELD = 256
MAX_LEN_USERS_CHARFIELD = 32
MIN_LEN_USERNAME = 3

MAX_LEN_RECIPES_CHARFIELD = 64
MAX_LEN_MEASUREMENT = 256
MAX_LEN_RECIPES_TEXTFIELD = 5000
MAX_LEN_TAGS_CHARFIELD = 64

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 300
MIN_AMOUNT_INGREDIENTS = 1
MAX_AMOUNT_INGREDIENTS = 32
MAX_M_UNIT_LENGTH = 24

SEARCH_ING_NAME = 'name'
FAVORITE = 'is_favorited'
SHOP_CART = 'is_in_shopping_cart'
AUTHOR = 'author'
TAGS = 'tags'
