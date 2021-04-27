@_default:
    just --list

# Docker
@build:
    docker-compose build

@build-sge-submit-host:
    docker-compose -f docker-compose-sge-submit-host.yml build

@down:
    docker-compose down

@up +ARGS="":
    docker-compose up {{ARGS}}

@watch:
    watch docker ps

# Django
@check:
    docker-compose run --rm django python manage.py check

@makemigrations:
    docker-compose run --rm django python manage.py makemigrations

@migrate:
    docker-compose run --rm django python manage.py migrate --noinput

@fmt:
    -black .
    -npx prettier --config=./prettier.config.js --write ./src/templates/

@manage +ARGS="--help":
    docker-compose run --rm django python manage.py {{ARGS}}

@lint:
    -black --check .
    -curlylint src/templates/
    -npx prettier --config=./prettier.config.js  --check ./src/templates/

@run +ARGS="":
    docker-compose run --rm django {{ARGS}}

@serve:
    docker-compose run --rm django python manage.py runserver

@shell:
    docker-compose run --rm django /bin/bash

@django-shell:
    docker-compose run --rm django python manage.py shell

@showmigrations:
    docker-compose run --rm django python manage.py showmigrations

@test +ARGS="":
    docker-compose run --rm django pytest -s {{ARGS}}

# Environment
@pip-compile:
    pip install --upgrade --requirement ./requirements.in
    pip-compile --rebuild ./requirements.in
