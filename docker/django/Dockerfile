FROM revolutionsystems/python:3.9.4-wee-optimized-lto

WORKDIR /app

ENV PYTHONUNBUFFERED 1
RUN python3.9 -m pip install -U pip

COPY requirements.txt /tmp/requirements.txt
RUN python3.9 -m pip install -U --no-cache-dir -r /tmp/requirements.txt

COPY docker/django/celery/beat_start.sh /start-scheduler
RUN chmod +x /start-scheduler

COPY docker/django/celery/flower_start.sh /start-flower
RUN chmod +x /start-flower

COPY docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

COPY ./src /app
