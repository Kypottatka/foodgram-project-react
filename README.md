# Краткое описание проекта Foodgram
Здесь должно быть описание проекта Foodgram
Ссылка на сайт: http://foodgram-tae.ddns.net/

## Данные для админ-зоны
логин - admin3@gmail.com
пароль - Qwerty123

## Для запуска приложения необходимо создать файл .env в корневой директории проекта со следующими переменными окружения:
```
SECRET_KEY='{string}' # очень длинная строка - секретный ключ Django
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```

## Инструкция по развертыванию проекта
Здесь должна быть инструкция

## Технологии

* Python 3.7
* Django 3.2
* DRF 3.12
* Simple JWT 4.7.2
* Djoser
* Docker
* Nginx
* Gunicorn
* Docker