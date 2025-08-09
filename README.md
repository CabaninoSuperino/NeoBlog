# Blog Lite

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-brightgreen)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST-3.14-green)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

REST API для блоговой платформы с JWT-аутентификацией, управлением постами и подпостами. Реализована массовая загрузка постов с вложенными подпостами, система лайков и просмотров.

## Требования
- Python 3.9+
- Docker и Docker Compose
- PostgreSQL 15+

## Установка и запуск

1. Клонирование репозитория
    ```bash
   git clone https://github.com/CabaninoSuperino/BlogLite.git
    cd BlogLite
    
3. Настройка переменных окружения
    ```bash
    Отредактируйте .env:
      
    SECRET_KEY=your_unique_secret_key  # Generate with: openssl rand -hex 32
    DB_NAME=blog
    DB_USER=django
    DB_PASSWORD=strong_password
    DB_HOST=db
    DB_PORT=5432
    DEBUG=True  # Set False in production


4. Запуск через Docker
    ```bash
    docker-compose up --build
    
5. Инициализация БД
    ```bash
    docker-compose exec app python manage.py migrate
    docker-compose exec app python manage.py createsuperuser
    
6. Локальная установка
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # .\venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    
  Документация API
  Доступна после запуска:
  
      http://localhost:8000/api/schema/swagger-ui/

Использование API
Аутентификация:

    curl -X POST http://localhost:8000/api/token/ \
      -H "Content-Type: application/json" \
      -d '{"username": "your_username", "password": "your_password"}'
    Используйте токен: Authorization: Bearer <access_token>

Эндпоинты
Посты	

        POST	/api/posts/	Создать пост (массово)
        GET	/api/posts/	Список постов
        GET	/api/posts/{id}/	Детали поста
        POST	/api/posts/{id}/like/	Поставить/снять лайк
        GET	/api/posts/{id}/view/	Увеличить просмотры

Подпосты

        POST	/api/subposts/	Создать подпост
        GET	/api/subposts/	Список подпостов
        GET	/api/subposts/{id}/	Детали подпоста

Пример запроса

        curl -X POST http://localhost:8000/api/posts/ \
          -H "Authorization: Bearer <token>" \
          -H "Content-Type: application/json" \
          -d '[
            {
              "title": "Post 1",
              "body": "Content 1",
              "subposts": [
                {"title": "Subpost 1.1", "body": "Content 1.1"},
                {"title": "Subpost 1.2", "body": "Content 1.2"}
              ]
            }
          ]'

        
Тестирование

        docker-compose exec app pytest
      # Или локально: pytest
      
Проверка кода

      ruff check .
      black --check .
      CI

GitHub Actions выполняет
- Тесты с покрытием ≥80%
- Линтинг (Ruff)
- Проверку форматирования (Black)


Администрирование:
  http://localhost:8000/admin/



