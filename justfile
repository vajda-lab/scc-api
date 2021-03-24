@_default:
    just --list

# Docker
build:
    docker-compose build

up:
    docker-compose up

down:
    docker-compose down

watch:
    watch docker ps

# Django
check:
    docker-compose run --rm django python manage.py check

makemigrations:
    docker-compose run --rm django python manage.py makemigrations

migrate:
    docker-compose run --rm django python manage.py migrate --noinput

run:
    docker-compose run --rm django python manage.py runserver

shell:
    docker-compose run --rm django /bin/bash

django-shell:
    docker-compose run --rm django python manage.py shell

showmigrations:
    docker-compose run --rm django python manage.py showmigrations

test +ARGS="":
    docker-compose run --rm django pytest -s {{ARGS}}

# Environment
upgrade-pip-requirements:
    pip install --upgrade --requirement ./requirements/base.in
    pip install --upgrade --requirement ./requirements/development.in
    pip-compile --rebuild ./requirements/base.in
    pip-compile --rebuild ./requirements/development.in
