# ==============================================================================
# STAGE 1: Builder - Install dependencies and build wheels
# ==============================================================================
# Digest-pinned base image (CICD-SEC-9: Improper Artifact Integrity Validation).
# Verify/refresh via: docker manifest inspect python:3.13-slim
FROM python:3.13-slim@sha256:eb43ff125d8d58d7449dcba7d336c23bcac412f526d861db493b9994d8010280 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_REQUESTS_TIMEOUT=120 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5

WORKDIR /app

# Install system dependencies required for building Python packages (e.g. psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry matching the project configuration
RUN pip install --no-cache-dir "poetry>=2.0.0"

# Copy package requirements files
COPY pyproject.toml poetry.lock ./

# Build dependencies only (cached layer).
# INSTALL_DEV=true for CI/test images; production builds must pass INSTALL_DEV=false.
ARG INSTALL_DEV=true
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    if [ "$INSTALL_DEV" = "true" ]; then \
      poetry install --with dev --no-root; \
    else \
      poetry install --only main --no-root; \
    fi

# ==============================================================================
# STAGE 2: Production Run-time Environment
# ==============================================================================
# Digest-pinned base image (CICD-SEC-9: Improper Artifact Integrity Validation).
# Verify/refresh via: docker manifest inspect python:3.13-slim
FROM python:3.13-slim@sha256:eb43ff125d8d58d7449dcba7d336c23bcac412f526d861db493b9994d8010280 AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    RECEIPT_PDF_ARTIFACT_DIR=/app/var/receipt-artifacts \
    PYTEST_CACHE_DIR=/app/var/pytest-cache \
    PATH="/app/.local/bin:${PATH}" \
    PORT=8000

WORKDIR /app

# Install minimal run-time system dependencies (like libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a secure, non-privileged user and group
RUN groupadd -g 10001 django-group && \
    useradd -u 10001 -g django-group -s /sbin/nologin -d /app django-user

# Copy installed site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY --chown=django-user:django-group . .

# Set strict permissions - root directory read-only for django-user
RUN chmod -R 755 /app && \
    mkdir -p /app/var/receipt-artifacts /app/var/pytest-cache && \
    chown -R django-user:django-group /app/var && \
    chmod -R 750 /app/var

# Switch to the non-root execution context
USER django-user

# Expose the API port
EXPOSE 8000

# Healthcheck for general container status
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f -H "X-Forwarded-Proto: https" http://localhost:8000/health/ || exit 1

# Run the Django production application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]
