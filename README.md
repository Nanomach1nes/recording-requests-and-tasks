# Система учёта заявок и задач организации

Fullstack-приложение на **FastAPI**, **Jinja2**, **SQLAlchemy** и **Bootstrap** для учёта ремонтных заявок, задач, категорий и комментариев. Проект можно открыть через браузер, использовать как REST API, запускать локально или через Docker.

## Возможности

- регистрация и авторизация пользователей;
- разделение ролей: обычный пользователь видит свои заявки, администратор может управлять заявками;
- создание, просмотр, поиск и фильтрация заявок;
- карточка заявки с контактными данными, статусом и комментариями;
- REST API для заявок, задач, категорий и комментариев;
- база данных со связями между пользователями, заявками, категориями, задачами и комментариями;
- автоматические тесты и GitHub Actions CI.

## Структура проекта

```
recording-requests-and-tasks/
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа приложения
│   ├── database.py       # Подключение к БД и сессии SQLAlchemy
│   ├── models/           # Модели SQLAlchemy
│   │   ├── __init__.py
│   │   ├── request.py
│   │   └── task.py
│   ├── schemas/          # Схемы Pydantic
│   │   ├── __init__.py
│   │   ├── request.py
│   │   └── task.py
│   └── routes/           # Эндпоинты API
│       ├── __init__.py
│       ├── requests.py
│       └── tasks.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy 2
- Pydantic 2
- Jinja2
- Bootstrap 5
- SQLite для локального запуска по умолчанию
- PostgreSQL в Docker Compose
- Pytest

## Требования

- Python 3.11+
- pip
- Docker и Docker Compose для контейнерного запуска

## Локальный запуск

1. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите сервер:

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

Браузерный интерфейс:

- вход: http://127.0.0.1:8000/ui/login
- регистрация: http://127.0.0.1:8000/ui/register
- журнал заявок: http://127.0.0.1:8000/ui/requests

Документация Swagger UI: http://127.0.0.1:8000/docs

По умолчанию локально используется SQLite-файл `app.db`. Для PostgreSQL задайте переменную окружения `DATABASE_URL` или создайте локальный файл `.env`, например:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:1@localhost:5432/recording_db
SECRET_KEY=local-development-secret-key
```

На текущем рабочем ПК проект настроен через `.env` на базу `recording_db` в локальном PostgreSQL.

## Запуск в Docker

```bash
docker compose up --build
```

Команда поднимает PostgreSQL и FastAPI-приложение. После запуска сайт доступен на http://127.0.0.1:8000

## Тестирование

```bash
pytest
```

Таблица тест-кейсов находится в `docs/test-cases.md`. В проекте покрыты основные сценарии: регистрация, вход, создание и просмотр заявок, изменение статуса, поиск, фильтрация, категории, задачи и комментарии.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работоспособности |
| GET | `/api/v1/requests/` | Список заявок |
| POST | `/api/v1/requests/` | Создание заявки |
| GET | `/api/v1/requests/{id}` | Получение заявки |
| PATCH | `/api/v1/requests/{id}` | Обновление заявки |
| DELETE | `/api/v1/requests/{id}` | Удаление заявки |
| GET | `/api/v1/tasks/` | Список задач |
| POST | `/api/v1/tasks/` | Создание задачи |
| GET | `/api/v1/tasks/{id}` | Получение задачи |
| PATCH | `/api/v1/tasks/{id}` | Обновление задачи |
| DELETE | `/api/v1/tasks/{id}` | Удаление задачи |
| GET | `/api/v1/categories/` | Список категорий |
| POST | `/api/v1/categories/` | Создание категории |
| GET | `/api/v1/comments/request/{id}` | Комментарии заявки |
| POST | `/api/v1/comments/` | Создание комментария |

## База данных

Структура описана в SQL-скрипте `app/database/schema.sql`. Минимальный набор таблиц:

- `users` — пользователи и роли;
- `categories` — категории заявок;
- `requests` — заявки;
- `tasks` — связанные задачи;
- `comments` — комментарии к заявкам.

## CI/CD и деплой

CI настроен в `.github/workflows/ci.yml`: при push или pull request устанавливаются зависимости и запускаются тесты.

Для публикации можно использовать Render или Railway. Для Render типовой запуск:

- build command: `pip install -r requirements.txt`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Ссылку на опубликованную версию нужно добавить в отчёт после деплоя.
