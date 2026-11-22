FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8003

COPY shared/ /tmp/shared/
COPY services/realtime-sync-service/requirements.txt .
RUN pip install --no-cache-dir /tmp/shared -r requirements.txt && rm -rf /tmp/shared

COPY services/realtime-sync-service/app/ ./app/

RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8003
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
