#!/usr/bin/env sh

PG_DB=webdev21videos2
PG_PASSWORD=`head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 12`
PG_SERVICE_NAME=postgres
PG_USER=webdev21videos2_user

echo "DEBUG=true
SECRET_KEY=`head -c 75 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 50`
POSTGRES_DB=$PG_DB
POSTGRES_PASSWORD=$PG_PASSWORD
POSTGRES_USER=$PG_USER
DATABASE_URL=postgres://$PG_USER:$PG_PASSWORD@$PG_SERVICE_NAME:5432/$PG_DB
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_FLOWER_USER=awake
CELERY_FLOWER_PASSWORD=awake" > .docker-env
