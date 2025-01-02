# Используем официальный образ Python
FROM python:3.12.3-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY ./requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Копируем код приложения внутрь контейнера
COPY ./ ./

ENV PYTHONUNBUFFERED=1

# Открываем порт приложения (по желанию)
EXPOSE 8000

# Запускаем приложение
CMD ["fastapi", "run", "main.py", "--port", "8000"]
