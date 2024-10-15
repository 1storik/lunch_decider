# Lunch Decider

## Описание проекта
Lunch Decider — это веб-приложение, которое помогает пользователям выбирать место для обеда. Проект разработан с использованием Django и PostgreSQL.

## Требования
- Docker
- Docker Compose
- Python 3.9 (в контейнере)

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL_вашего_репозитория>
   cd lunch_decider

2. **Соберите и запустите контейнеры:**
   ```bash
   docker-compose up --build

3. **Для запуска тестов используйте команду:**
   ```bash
   docker-compose exec web pytest

4. **Миграции базы данных:**
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser