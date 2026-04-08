FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY main.py .
COPY static ./static

# Добавлен пакет requests
RUN pip install fastapi uvicorn psycopg2-binary pydantic requests python-docx python-multipart httpx pyTelegramBotAPI

EXPOSE 8000

CMD ["sh", "-c", "python3 telegram_polling.py & uvicorn main:app --host 0.0.0.0 --port 8000"]
