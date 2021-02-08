@_default:
    just --list

build:
  	docker-compose build

up:
    docker-compose up

upgrade-pip-requirements:
  	pip install -U -r ./requirements/base.in
  	pip-compile -r ./requirements/base.in
  	pip-compile -r ./requirements/development.in
