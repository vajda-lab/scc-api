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
    POSTGRES_HOST=$PG_SERVICE_NAME
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

@bump:
    bumpver update

@deploy +ARGS="":
    rsync -av \
        {{ ARGS }} \
        --exclude '__pycache__' \
        --exclude '.docker-env*' \
        --exclude '.DS_Store' \
        --exclude '.github' \
        --exclude '.gitignore' \
        --exclude '.pytest_cache' \
        --exclude '*.bz2' \
        --exclude '*.git' \
        --exclude '*.pyc' \
        --exclude '*.xz' \
        --exclude 'celerybeat*' \
        --exclude 'docker-compose.yml' \
        --exclude 'justfile' \
        . \
        ftplus-dev.bu.edu:/srv/scc-api

# Deploy & Build Django app on ftplus sites
@deploy-build:
    just deploy
    # ssh ftplus-dev.bu.edu 'cd /srv/scc-api && docker-compose build && docker-compose down && docker-compose up -d'
    ssh ftplus-dev.bu.edu 'cd /srv/scc-api && docker-compose build && docker-compose stop django scheduler worker && docker-compose start django scheduler worker'

# Stops containers
@down:
    docker-compose down

# Starts containers; also takes arguments
@up +ARGS="":
    docker-compose up {{ ARGS }}

# Monitors container status
@watch:
    watch docker ps

# Uses Django System Check Framework to inspect project for common problems
@check:
    docker-compose run --rm django python manage.py check

# Runs Django command in container
@makemigrations:
    docker-compose run --rm django python manage.py makemigrations

# Runs Django command in container
@migrate:
    docker-compose run --rm django python manage.py migrate --noinput

# Runs Black
@fmt:
    -black .
    -djhtml --in-place src/templates/*.html src/templates/**/*.html

# Runs Django's manage.py in container; takes arguments
@manage +ARGS="--help":
    docker-compose run --rm django python manage.py {{ ARGS }}

# Runs code and template linters
@lint:
    -black --check .
    -djhtml --check src/templates/*.html src/templates/**/*.html

@run +ARGS="":
    docker-compose run --rm django {{ ARGS }}

# Runs Django runserver in container
@serve:
    docker-compose run --rm django python manage.py runserver

# Starts Bash in Django container
@shell:
    docker-compose run --rm django /bin/bash

# Starts Django shell in container
@django-shell:
    docker-compose run --rm django python manage.py shell

# Runs Django showmigrations in container
@showmigrations:
    docker-compose run --rm django python manage.py showmigrations

# Runs pytest in container
@test +ARGS="":
    docker-compose run --rm django pytest -s {{ ARGS }}

# Builds upgraded requirements.txt from requirements.in
@pip-compile:
    pip install --upgrade -r ./requirements.in
    # pip-compile ./requirements.in
    docker-compose run --rm django \
        rm -f ./requirements.txt && \
        pip install -U pip pip-tools && \
        pip install \
            --upgrade \
            --requirement ./requirements.in && \
        pip-compile \
            ./requirements.in \
            --output-file ./requirements.txt
