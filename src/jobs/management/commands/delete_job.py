import djclick as click

from jobs.tasks import delete_job


@click.command()
@click.option("--pk", required=True)
def main(pk):
    delete_job.delay(pk=pk)
