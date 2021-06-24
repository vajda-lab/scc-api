import djclick as click

from jobs.tasks import update_job_priority


@click.command()
@click.option("--pk", required=True)
@click.option("--new-priority", required=True)
def command(new_priority, pk):
    update_job_priority.delay(pk=pk, new_priority=new_priority)
