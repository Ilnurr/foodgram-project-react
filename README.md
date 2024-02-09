# Продуктовый помощник - Foodgram

## Описание
Foodgram - продуктовый помощник, который позволяет пользователям публиковать свои рецепты, добавлять рецепты в избранное, подписываться на публикации других авторов и скачивать список продуктов, необходимых для приготовления выбранных блюд.

## Стек технология:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

## Запуск проекта с помощью Docker:

Клонируйте репозиторий:
```
git clone git@github.com:Ilnurr/foodgram-project-react.git
```
Создайте файл .env в корневой директории проекта и добавьте следующие строки:
```
SECRET_KEY = 'YOUR_SECRET_KEY' #Унимкальный ключ
ALLOWED_HOSTS = 'YOUR_DOMAIN_NAME' #Доменное имя 
DB_NAME=postgres 
POSTGRES_USER=postgres 
POSTGRES_PASSWORD=postgres 
DB_HOST=db 
DB_PORT=5432 
```
В папке проекта выполните следующую команду:
```
sudo docker-compose up -d 
```
Выполните миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
Выполните сбор статики:
```
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker-compose -f docker-compose.production.yml exec backend cp -r collect_static/. ../static_backend/static_backend/
```
Создайте суперпользователя:
```
sudo docker-compose exec web python manage.py createsuperuser
```
Загрузите данные в базу данных:
```
sudo docker-compose exec backend python manage.py loaddata dump.json
```
Теперь проект доступен по адресу:
```
http://127.0.0.1:8080
```
## Cайт временно доступен по ссылке:
- URL: http://fgrm.ddns.net/
- login: admin@mail.ru
- Pas: admin
