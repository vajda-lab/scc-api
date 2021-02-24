@_default:
    just --list

build:
    docker-compose build

up:
    docker-compose up

upgrade-pip-requirements:
    pip install --upgrade --requirement ./requirements/base.in
    pip install --upgrade --requirement ./requirements/development.in
    pip-compile --rebuild ./requirements/base.in
    pip-compile --rebuild ./requirements/development.in

test:
	# docker-compose run --rm django pytest
	docker-compose run --rm django pytest -x

shell:
	docker-compose run --rm django /bin/bash