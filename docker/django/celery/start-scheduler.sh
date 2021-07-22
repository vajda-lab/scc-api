#!/bin/sh

set -o errexit
set -o nounset

celery -A config beat -l INFO --pidfile=
