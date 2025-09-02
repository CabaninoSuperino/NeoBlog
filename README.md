# NeoBlog

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
   git clone https://github.com/CabaninoSuperino/NeoBlog.git
    cd BlogLite
    
3. Настройка переменных окружения
    ```bash
    Отредактируйте .env:
      
    SECRET_KEY=your_unique_secret_key  
    DB_NAME=blog
    DB_USER=django
    DB_PASSWORD=strong_password
    DB_HOST=db
    DB_PORT=5432
    DEBUG=True  # Set False in production




