
#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Checking Django configuration..."
python manage.py check

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Checking migration status..."
python manage.py showmigrations newsapp

echo "Build completed successfully."
