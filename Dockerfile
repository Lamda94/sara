# Stage 1: Builder
FROM python:3.12-slim AS builder

RUN pip install uv

WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN uv pip install --system .

# Stage 2: Runtime
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY src/ src/

ENV PYTHONPATH=/app/src
ENV PORT=10000

CMD ["sh", "-c", "uvicorn sara.main:app --host 0.0.0.0 --port ${PORT}"]
