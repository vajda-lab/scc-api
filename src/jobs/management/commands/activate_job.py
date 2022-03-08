import djclick as click

from jobs.tasks import activate_job


@click.command()
@click.option("--pk", required=True)
def command(pk):
    activate_job.delay(pk=pk)
