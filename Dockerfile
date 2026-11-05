# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем переменные окружения, чтобы Python не писал файлы .pyc и сразу выводил логи
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем и устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для сборки psycopg2 (из вашего примера)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей Django
COPY requirements.txt ./

# Обновляем pip и устанавливаем библиотеки проекта
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Создаем папку для медиафайлов из вашего примера
RUN mkdir -p /app/media

# Документируем порт приложения (критерий: использование expose для веб-сервиса внутри сети)
EXPOSE 8000