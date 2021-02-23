@_default:
    just --list

build:
    docker-compose build

up:
    docker-compose up

upgrade-pip-requirements:
    pip install -U -r ./requirements/base.in
    pip install -U -r ./requirements/development.in
    -pip-compile -r ./requirements/base.in
    -pip-compile -r ./requirements/development.in

test:
	docker-compose run --rm django pytest
#	docker-compose run --rm django pytest -x

shell:
	docker-compose run --rm django /bin/bash