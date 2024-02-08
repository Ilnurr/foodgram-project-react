# Продуктовый помощник - Foodgram

## Описание
Foodgram - это продуктовый помощник, который позволяет пользователям публиковать свои рецепты, добавлять рецепты в избранное, подписываться на публикации других авторов и скачивать список продуктов, необходимых для приготовления выбранных блюд.

Стек технология:

## Запуск проекта на локальной машине с помощью Docker
Склонируйте репозиторий на свою локальную машину:
```
git clone git@github.com:Ilnurr/foodgram-project-react.git
```
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
```
В папке проекта выполните следующую команду:
sudo docker-compose up -d 
```
Выполните миграции:
sudo docker-compose exec backend python manage.py migrate
```
Выполните сбор статики:
sudo docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker-compose -f docker-compose.production.yml exec backend cp -r collect_static/. ../static_backend/static_backend/
```
Создайте суперпользователя:
sudo docker-compose exec web python manage.py createsuperuser
```
Загрузите данные в базу данных:
sudo docker-compose exec backend python manage.py loaddata dump.json
```
Теперь проект доступен по адресу:
http://127.0.0.1:8080
```
## Cайт временно доступен по ссылке:
- URL: http://fgrm.ddns.net/
- login: admin@mail.ru
- Pas: admin
