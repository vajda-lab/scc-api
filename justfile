@_default:
    just --list

bootstrap:
    #!/usr/bin/env bash
    set -euxo pipefail
    PG_DB=webdev21videos2
    PG_PASSWORD=`head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 12`
    PG_SERVICE_NAME=postgres
    PG_USER=webdev21videos2_user
    FILE=.docker-env
    if [ ! -f "$FILE" ]; then
        echo "$FILE created"
        echo "ALLOWED_HOSTS=*
    CELERY_BROKER_URL="redis://redis:6379/0"
    CELERY_FLOWER_PASSWORD=awake
    CELERY_FLOWER_USER=awake
    DATABASE_URL="postgres://$PG_USER:$PG_PASSWORD@$PG_SERVICE_NAME:5432/$PG_DB"
    DEBUG=true
    GRID_ENGINE_DELETE_CMD=/app/bin/qdel
    GRID_ENGINE_STATUS_CMD=/app/bin/qstat
    GRID_ENGINE_SUBMIT_CMD=/app/bin/qsub
    POSTGRES_DB=$PG_DB
    POSTGRES_PASSWORD=$PG_PASSWORD
    POSTGRES_USER=$PG_USER
    REDIS_URL="redis://redis:6379/0"
    SCC_FTPLUS_PATH=/tmp/
    SCC_MAX_HIGH_JOBS=50
    SCC_MAX_LOW_JOBS=25
    SCC_MAX_NORMAL_JOBS=25
    SECRET_KEY=`head -c 75 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 50`" > $FILE
    fi

# Build Docker images
@build:
    docker-compose build

# Build Sun Grid Engine Submit Host images
@build-sge-submit-host:
    docker-compose -f docker-compose-sge-submit-host.yml build

@down:
    docker-compose down

# Starts containers; also takes arguments
@up +ARGS="":
    docker-compose up {{ARGS}}

# Monitors container status
@watch:
    watch docker ps

# Uses Django system check framework to inspect project for common problems
@check:
    docker-compose run --rm django python manage.py check

@makemigrations:
    docker-compose run --rm django python manage.py makemigrations

@migrate:
    docker-compose run --rm django python manage.py migrate --noinput

@fmt:
    -black .

@manage +ARGS="--help":
    docker-compose run --rm django python manage.py {{ARGS}}

@lint:
    -black --check .
    -curlylint src/templates/

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

# Builds upgraded requirements.txt from requirements.in
@pip-compile:
    # pip install --upgrade --requirement ./requirements.in
    pip-compile --upgrade ./requirements.in
    # pip-compile --rebuild ./requirements.in
