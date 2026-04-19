# 🎯 Трекер полезных привычек

Бэкенд-часть SPA веб-приложения для отслеживания полезных привычек, основанная на книге Джеймса Клира «Атомные привычки».

## 📋 О проекте

Приложение позволяет пользователям создавать, отслеживать и анализировать свои привычки. Основная идея — формирование полезных привычек через регулярное выполнение небольших действий с системой вознаграждений.

### Основные возможности

- ✅ Создание и управление привычками (CRUD)
- 🔔 Автоматические напоминания через Telegram-бота
- 📊 Отслеживание серий выполнения (streak)
- 👥 Публичные привычки для вдохновения
- 📈 Статистика и аналитика выполнения
- 🔒 JWT-аутентификация
- 📱 REST API с пагинацией

## 🚀 Технологии

- **Python** 3.11
- **Django** 4.2
- **Django REST Framework** 3.14
- **PostgreSQL** / SQLite
- **Celery** 5.3
- **Redis** 7.4
- **JWT** аутентификация
- **Telegram Bot API**
- **Docker** (опционально)


## 🛠 Установка и запуск

### Требования

- Python 3.11 или выше
- PostgreSQL (или SQLite для разработки)
- Redis (для Celery)
- Telegram Bot Token

## Шаг 1. Клонирование репозитория

- git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker

## Шаг 2. Создание виртуального окружения

### Через venv
- python -m venv venv
- source venv/bin/activate  # Linux/MacOS
- venv\Scripts\activate     # Windows

### Или через poetry
- poetry shell

## Шаг 3. Установка зависимостей

- pip install -r requirements.txt
### или
- poetry install

## Шаг 4. Настройка переменных окружения

env
### Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

### Database (PostgreSQL)
DB_NAME=habit_tracker_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

### Redis (для Celery)
REDIS_URL=redis://localhost:6379/0

### Telegram
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_NAME=your_bot_name

## Шаг 5. Настройка базы данных

### Создание миграций
python manage.py makemigrations
python manage.py migrate

### Создание суперпользователя
python manage.py createsuperuser

## Шаг 6. Запуск сервера

python manage.py runserver

## Шаг 7. Запуск Celery и Redis

### Терминал 1: Redis
redis-server
### или
brew services start redis

### Терминал 2: Celery Worker
celery -A config worker -l info

### Терминал 3: Celery Beat (для периодических задач)
celery -A config beat -l info

## Пример запроса

### Регистрация
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123","password_confirm":"pass123"}'

### Создание привычки
curl -X POST http://localhost:8000/api/habits/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "Утренняя зарядка",
    "place": "Дома",
    "time": "07:00:00",
    "duration_seconds": 60,
    "periodicity": 1,
    "reward": "Вкусный завтрак"
  }'

## Лицензия
- Этот проект создан в рамках курсовой работы.

## Автор
- Аведян Амаяк