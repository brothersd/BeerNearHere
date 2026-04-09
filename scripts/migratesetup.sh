#!/bin/bash

echo "Waiting for database to be ready..."
until docker compose exec web python manage.py showmigrations > /dev/null 2>&1; do
    echo "  DB not ready, retrying in 2 seconds..."
    sleep 2
done
echo "Database is ready!"

docker compose exec web python manage.py makemigrations stores
sleep 3
docker compose exec web python manage.py migrate
sleep 3
docker compose exec web python manage.py createsuperuser