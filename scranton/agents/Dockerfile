FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

RUN uv pip install -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" venkat && \
    chown -R venkat:venkat /app

USER venkat

ENV PATH="/home/venkat/.local/bin:$PATH"

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT"]