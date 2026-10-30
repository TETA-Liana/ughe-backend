#!/bin/sh
# Start-up script used by the backend Docker container.
set -e

echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT ..."
python - <<'PY'
import os, time, psycopg2
for attempt in range(60):
    try:
        psycopg2.connect(dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
                         password=os.environ["POSTGRES_PASSWORD"], host=os.environ["POSTGRES_HOST"],
                         port=os.environ.get("POSTGRES_PORT", "5432")).close()
        print("PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    raise SystemExit("PostgreSQL did not become ready in time.")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_ughe

exec python manage.py runserver 0.0.0.0:8000
