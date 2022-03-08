import djclick as click

from jobs.tasks import scheduled_allocate_job


@click.command()
def command():
    scheduled_allocate_job.delay()
