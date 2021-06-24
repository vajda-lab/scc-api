import djclick as click

from jobs.tasks import scheduled_allocate_job


@click.command()
def main():
    scheduled_allocate_job.delay()
