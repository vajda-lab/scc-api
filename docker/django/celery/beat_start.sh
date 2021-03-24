#!/bin/sh

set -o errexit
set -o nounset


rm -f './scheduler.pid'
celery -A config beat -l INFO
