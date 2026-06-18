# Система учёта заявок и задач

REST API на **FastAPI** для создания заявок и управления связанными с ними задачами.

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

## Требования

- Python 3.12+
- pip

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

Документация Swagger UI: http://127.0.0.1:8000/docs

## Запуск в Docker

Сборка образа:

```bash
docker build -t requests-tasks-api .
```

Запуск контейнера:

```bash
docker run -p 8000:8000 requests-tasks-api
```

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

## База данных

По умолчанию используется SQLite (`app.db` в корне проекта). Для PostgreSQL измените строку подключения в `app/database.py` и установите переменные окружения при необходимости.
