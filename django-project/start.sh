
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn YOUR_PROJECT.wsgi:application --bind 0.0.0.0:$PORT
