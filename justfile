@_default:
    just --list

bootstrap:
    #!/usr/bin/env bash
    # set -euxo pipefail
    PG_DB=webdev21videos2
    PG_PASSWORD=`head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 12`
    PG_SERVICE_NAME=postgres
    PG_USER=webdev21videos2_user
    FILE=.docker-env
    if [ ! -f "$FILE" ]; then
        echo "$FILE created"
        echo "CELERY_BROKER_URL="redis://redis:6379/0"
    CELERY_FLOWER_PASSWORD=awake
    CELERY_FLOWER_USER=awake
    DATABASE_URL="postgres://$PG_USER:$PG_PASSWORD@$PG_SERVICE_NAME:5432/$PG_DB"
    DEBUG=true
    POSTGRES_DB=$PG_DB
    POSTGRES_PASSWORD=$PG_PASSWORD
    POSTGRES_USER=$PG_USER
    REDIS_URL="redis://redis:6379/0"
    SECRET_KEY=`head -c 75 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 50`" > $FILE
    fi

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
