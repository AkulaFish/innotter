#!/usr/bin/env sh
set -ex
python manage.py makemigrations users
python manage.py makemigrations core
python manage.py migrate
python manage.py runserver 0.0.0.0:8000