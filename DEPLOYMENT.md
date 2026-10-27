# Deployment guide

For the step-by-step Render deployment, read **`README_RENDER.md`** first.

Run Django commands from this directory (the directory containing `manage.py`).

The default Render Blueprint uses PostgreSQL via `DATABASE_URL`; the Django settings also support MySQL when `DB_ENGINE=mysql` and `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` are set. A MySQL/MariaDB SQL dump is not directly importable into PostgreSQL. See `README_RENDER.md` for the safe options and migration warning.

Never commit `.env`, `database/newspythondb.sql`, local database files, or secrets to Git. The SQL dump contains historical user records and password hashes; keep it private.
