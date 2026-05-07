# Dockerfile for BrainCell REST API Service
# Build context: repo root (ITL.BrainCell.Api/)
# itl-braincell core library is installed from PyPI.
FROM python:3.12-alpine AS builder

WORKDIR /build

RUN apk add --no-cache build-base postgresql-dev

RUN pip install --no-cache-dir --target ./python-packages itl-braincell

# ========== Runtime Stage ==========
FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache postgresql-client curl

COPY --from=builder /build/python-packages /usr/local/lib/python3.12/site-packages

# Copy API-specific code
COPY src/api src/api
COPY src/main.py src/main.py
COPY src/__init__.py src/__init__.py

# Copy Alembic configuration and migrations
COPY alembic.ini .
COPY alembic alembic

# Copy entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN addgroup braincell && adduser -D -G braincell braincell && \
    chown -R braincell:braincell /app

USER braincell

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
