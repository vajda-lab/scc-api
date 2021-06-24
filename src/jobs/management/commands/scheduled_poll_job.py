import djclick as click
from jobs.tasks import scheduled_poll_job


@click.command()
def main():
    scheduled_poll_job.delay()
