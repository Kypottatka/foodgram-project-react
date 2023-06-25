# Foodgram

![workflow](https://github.com/Kypottatka/foodgram-project-react/actions/workflows/main.yml/badge.svg)

***
[Вопросы](https://github.com/Kypottatka/foodgram-project-react/issues).
***

## Technologies

- Python 3.11
- Django 4.0
- Django REST framework 3.14
- Djoser
- Simple JWT 4.7.2
- React
- Nginx
- Gunicorn
- Docker
- Postgres

## http://foodgram-tae.ddns.net/

### To deploy this project, the following actions are needed

- Download project with SSH (actually you only need the folder 'infra/')

```text
git clone git@github.com:Kypottatka/foodgram-project-react.git
```

- Connect to your server:

```text
ssh <server user>@<server IP>
```

- Install Docker on your server

```text
sudo apt install docker.io
```

- Install Docker Compose (for Linux)

```text
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Get permissions for docker-compose

```text
sudo chmod +x /usr/local/bin/docker-compose
```

- Create project directory (preferably in your home directory)

```text
mkdir foodgram && cd foodgram/
```

- Create env-file:

```text
touch .env
```

- Fill in the env-file like this:

```text
DEBUG=False
SECRET_KEY=<Your_some_long_string>
ALLOWED_HOSTS=<Your_host>
CSRF_TRUSTED_ORIGINS=https://<Your_host>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Your_password>
DB_HOST=foodgram-db
DB_PORT=5432
```

- Copy files from 'infra/' (on your local machine) to your server:

```text
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```

- Run docker-compose

```text
sudo docker-compose up -d
```

Wait a few seconds... Your service should now be working!

**Enjoy your meal!**

Oh, I'm sorry. You also need to create the first account for the admin panel using this command:

```text
sudo docker exec -it app python manage.py createsuperuser
```

And if you want, you can use the list of ingredients that we offer to write recipes. Upload this list to the database using the following command:

```text
sudo docker exec -it foodgram-app python manage.py loaddata scripts/ingredients_transformed.json
```


### *Backend by:*

[Kypottatka](https://github.com/Kypottatka)