web: python manage.py migrate --noinput && python manage.py create_superadmin && python manage.py collectstatic --noinput && gunicorn darkshadow.wsgi:application --bind 0.0.0.0:$PORT
