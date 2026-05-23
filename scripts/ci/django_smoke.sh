#!/usr/bin/env bash
# ==============================================================================
# Django Production Smoke Test Validation Script
# ==============================================================================
# Strict execution mode: Fail immediately on any subcommand error or unset variables
set -euo pipefail

echo "[*] Booting Django Production Smoke Tests..."

# ------------------------------------------------------------------------------
# 1. ENFORCE PRODUCTION CONFIGURATION ENVIRONMENT
# ------------------------------------------------------------------------------
# We deliberately force DEBUG=False and pass mock credentials.
# This forces Django to validate production security checks, host headers,
# settings parsing, and database adapter loading, avoiding configuration drift.
export DEBUG="False"
export SECRET_KEY="django-insecure-smoke-test-production-dummy-key-extremely-long-and-secure-12345" # nosec
export ALLOWED_HOSTS="localhost,127.0.0.1,testserver,api.beautycosmetics.com"
export CORS_ALLOWED_ORIGINS="https://beautycosmetics.com,https://admin.beautycosmetics.com"

# Set fallback database connections (routed through Toxiproxy if running resilience profile)
export POSTGRES_DB="${POSTGRES_DB:-beauty_db}"
export POSTGRES_USER="${POSTGRES_USER:-beauty_user}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-beauty_secure_password}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export REDIS_URL="${REDIS_URL:-redis://:beauty_redis_secure_password@localhost:6379/0}"

echo "[*] Target settings configured. Running system validations..."

# ------------------------------------------------------------------------------
# 2. RUN DJANGO CORE SYSTEM CHECKS
# ------------------------------------------------------------------------------
echo "[*] Step 1: Running Django check --deploy..."
# Runs security, database, cache, and email checks tailored for production deployment.
python manage.py check --deploy

# ------------------------------------------------------------------------------
# 3. VERIFY PENDING DATABASE MIGRATIONS
# ------------------------------------------------------------------------------
echo "[*] Step 2: Checking for uncreated or untracked database migrations..."
# Fails the build if there are any model changes that have not been written to migrations.
python manage.py makemigrations --check --dry-run

# ------------------------------------------------------------------------------
# 4. HEADLESS MODULE AND ROUTING IMPORTS VALIDATION
# ------------------------------------------------------------------------------
echo "[*] Step 3: Executing headless checks for Celery and Routing modules..."
python -c "
import sys
import django

try:
    print('[+] Initializing Django engine...')
    django.setup()
    
    print('[+] Attempting to load URL Configurations...')
    from core.urls import urlpatterns
    print(f'[+] URL Configurations loaded successfully. Found {len(urlpatterns)} top-level paths.')
    
    print('[+] Attempting to import Celery App instance...')
    from core.celery import app as celery_app
    print('[+] Celery App initialized and imported successfully.')
    
except Exception as e:
    print(f'[-] Headless Smoke Test Import Failed: {e}', file=sys.stderr)
    sys.exit(1)
"

echo "[+] Django CI Smoke Test passed successfully. Framework is structurally sound."
exit 0
