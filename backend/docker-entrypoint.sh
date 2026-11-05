#!/bin/sh
# Migra la base, carga los datos de demostración (idempotente) y arranca la API.
set -e

alembic upgrade head

if [ "${RUN_SEED:-1}" = "1" ]; then
    python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
