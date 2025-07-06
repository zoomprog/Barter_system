# Barter System - Система обмена товарами

Django-приложение для создания объявлений и обмена товарами между пользователями.

## Установка и настройка

### 1. Создание виртуального окружения

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
# Установка основных зависимостей
pip install -r requirements.txt
```

### 3. Настройка базы данных PostgreSQL

# Создайте файл .env
```
DATABASE=DATABASE_NAME
USER=USER_NAME
PASSWORD=PASSWORD
````

```bash
# Применение миграций
cd exchange_project
python manage.py migrate
```
## Запуск проекта

```bash
# Запуск сервера разработки
python manage.py runserver
```

## Запуск тестов

### Запуск всех тестов

```bash
python -m pytest
```
