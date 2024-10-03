# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Открываем порт, на котором работает gRPC сервер
EXPOSE 23009

# Запускаем сервер при старте контейнера
CMD ["python", "src/grps_server.py"]