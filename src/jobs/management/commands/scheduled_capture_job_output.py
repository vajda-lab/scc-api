import djclick as click

from jobs.tasks import scheduled_capture_job_output


@click.command()
def command():
    scheduled_capture_job_output.delay()
