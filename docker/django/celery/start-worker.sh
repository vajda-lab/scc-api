#!/bin/sh

set -o errexit
set -o nounset

celery -A config worker --queues celery -l INFO
