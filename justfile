@_default:
    just --list

build:
    docker-compose build

check:
	docker-compose run --rm django python manage.py check

migrate:
	docker-compose run --rm django python manage.py migrate --no-input

run:
	docker-compose run --rm django python manage.py runserver

shell:
	docker-compose run --rm django /bin/bash

showmigrations:
	docker-compose run --rm django python manage.py showmigrations

test:
	# docker-compose run --rm django pytest
	docker-compose run --rm django pytest -x

up:
    docker-compose up

upgrade-pip-requirements:
    pip install --upgrade --requirement ./requirements/base.in
    pip install --upgrade --requirement ./requirements/development.in
    pip-compile --rebuild ./requirements/base.in
    pip-compile --rebuild ./requirements/development.in
