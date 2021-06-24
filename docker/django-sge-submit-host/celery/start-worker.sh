#!/bin/sh

set -o errexit
set -o nounset

su ftsubmit
celery -A config worker --queues celery -l INFO
