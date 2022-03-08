import djclick as click
from jobs.tasks import scheduled_poll_job


@click.command()
def command():
    scheduled_poll_job.delay()
