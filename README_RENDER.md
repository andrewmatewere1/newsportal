# News Portal — Render-ready project package

This folder is arranged so the **repository root is the Django project root**: `manage.py`, `requirements.txt`, `render.yaml`, and `build.sh` are at the top level.

## Recommended deployment (fresh PostgreSQL test database)

1. This test Blueprint requests Render free plans for the web service and PostgreSQL database. Free-plan availability and limits can change; check Render before applying. No persistent media disk is configured, so uploaded files may be lost after redeploy/restart. For durable uploads, configure S3-compatible object storage or upgrade to a persistent disk.
2. Create a **private** GitHub repository.
3. Copy/upload the contents of this folder to the repository root. Do not upload `.env`, local database files, or `database/newspythondb.sql` to Git. `.gitignore` excludes them.
4. In Render, choose **New → Blueprint**, connect the repository, and apply `render.yaml`.
5. Wait for the build and migration commands to finish. Open the service logs if a step fails.
6. Check the actual Render hostname. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in the Render environment if the hostname differs from `news-portal-django.onrender.com`.
7. Create an administrator using the Render Shell where available: `python manage.py createsuperuser`. Verify the custom dashboard's `user_type` role separately; Django superuser status and the custom application's primary-admin role are not necessarily the same.
8. Test homepage, article pages, search, login/permissions, comments, advertisements, social links, image uploads, and mobile layout.

## Database: important MySQL vs PostgreSQL note

The included `database/newspythondb.sql` is a historical **MariaDB/MySQL** export. The included Render Blueprint creates **PostgreSQL**. These are different database engines, and Django does not convert or import a MySQL SQL dump into PostgreSQL automatically. **Do not import this `.sql` file into Render PostgreSQL.**

For the simplest deployment, use the PostgreSQL database created by Render and let the pre-deploy command run `python manage.py migrate`. This gives you a fresh database; it does not automatically restore the articles/users from the historical MySQL dump.

If preserving the existing MySQL data is required, use a separately hosted MySQL/MariaDB service and configure the Render web service with these environment variables instead:

- `DB_ENGINE=mysql`
- `DB_NAME` = database name
- `DB_USER` = database username
- `DB_PASSWORD` = database password
- `DB_HOST` = provider's database hostname
- `DB_PORT` = provider's port (usually `3306`)

In that setup, remove/omit the `DATABASE_URL` variable from the web service because `DATABASE_URL` takes precedence in `settings.py`. The database host must allow connections from Render. Import the SQL dump into a **separate empty test database**, not into a live database, and verify schema compatibility with migrations first. This dump is from 2024 and predates the current advertisement migrations; direct import may require a careful migration/restore plan. Never assume it is safe to run `migrate` on the imported schema without testing.

The SQL file contains historical user/account records and password hashes. Keep it private and do not commit it to a public repository. Consider changing/resetting old accounts before using restored data publicly.

## Uploaded media

The ZIP may include existing `media/` files for local reference, but `.gitignore` excludes them from Git. This free test configuration has no persistent media disk. Files uploaded to the web service filesystem may disappear on redeploy/restart. For durable uploads, configure S3-compatible object storage using the documented AWS_* environment variables, or upgrade and configure a persistent disk.

## Environment variables

Use Render's environment settings for `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and the database connection. Configure `SOCIAL_FACEBOOK_URL`, `SOCIAL_X_URL`, `SOCIAL_INSTAGRAM_URL`, and `SOCIAL_WHATSAPP_URL` with the publisher's real links. Do not commit a real `.env` file.

## Local run (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Use local-only secrets in `.env`. Do not use `DEBUG=True` on a public deployment.

## Deployment validation status

This package reorganizes the files and supplies deployment instructions; it does not claim that the hosted service has already been deployed or browser-tested. Run Django checks and test the live site after deployment.
