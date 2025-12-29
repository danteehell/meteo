
python manage.py migrate --noinput

rm -rf staticfiles/*

python manage.py collectstatic --noinput

gunicorn meteo.wsgi:application --bind 0.0.0.0:$PORT
