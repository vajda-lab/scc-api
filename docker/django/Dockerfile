FROM revolutionsystems/python:3.6.8-wee-optimized-lto

WORKDIR /app

ENV PYTHONUNBUFFERED 1
RUN python3.6 -m pip install -U pip setuptools

COPY requirements /tmp/requirements
RUN python3.6 -m pip install -U --no-cache-dir -r /tmp/requirements/development.txt

COPY docker/django/celery/beat_start.sh /start-celerybeat
RUN chmod +x /start-celerybeat

COPY docker/django/celery/flower_start.sh /start-flower
RUN chmod +x /start-flower

COPY docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]