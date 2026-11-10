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

# Создаем папки для статических и медиафайлов, даем права
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles
RUN mkdir -p /app/media && chmod -R 755 /app/media

# Документируем порт приложения
EXPOSE 8000

# собираем статику и включаем промышленный сервер
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]