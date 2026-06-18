# Используем стабильный легковесный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /code

# Запрещаем Python писать файлы .pyc на диск и буферизировать логи
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем файл зависимостей (если его еще нет, мы его сейчас создадим)
COPY ./requirements.txt /code/requirements.txt

# Устанавливаем системные зависимости и библиотеки Python
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Копируем остальной код проекта в контейнер
COPY . /code

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска приложения через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]