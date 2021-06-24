FROM revolutionsystems/python:3.8.9-wee-optimized-lto

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python3 -m pip install -U pip

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -U --no-cache-dir -r /tmp/requirements.txt

COPY docker/django/celery/start-scheduler.sh /start-scheduler.sh
RUN chmod +x /start-scheduler.sh

COPY docker/django/celery/start-worker.sh /start-worker.sh
RUN chmod +x /start-worker.sh

COPY docker/django/celery/start-flower.sh /start-flower.sh
RUN chmod +x /start-flower.sh

COPY docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY ./src /app

ENTRYPOINT ["entrypoint.sh"]
