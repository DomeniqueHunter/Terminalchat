FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CURSED_DATA=/data \
    CURSED_PORT=6969

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cursed_descent ./cursed_descent
COPY start-container.sh .
RUN chmod +x start-container.sh \
    && mkdir -p /data \
    && chown -R 1000:1000 /app /data

USER 1000:1000

EXPOSE 6969
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"CURSED_PORT\"]}/health')"
ENTRYPOINT ["./start-container.sh"]
