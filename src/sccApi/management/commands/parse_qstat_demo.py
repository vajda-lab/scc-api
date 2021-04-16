import pytz
import djclick as click

from dateutil import tz
from dateutil.parser import parse
from django.conf import settings
from django.utils.dateparse import parse_datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

from sccApi.models import Job
from user_app.models import User


def parse_output(output):
    lines = [line for line in output.split("\n") if len(line)]
    header_keys = [column for column in lines[0].split(" ") if len(column)]
    print(header_keys)
    # print(header.split(" "))
    rows = []
    for row in lines[2:]:
        data = {}
        columns = [column for column in row.split(" ") if len(column)]
        for column in range(len(columns)):
            data[header_keys[column]] = columns[column]
        rows.append(data)
    return rows


@click.command()
@click.argument("input_filename")
def main(input_filename):

    if Path(input_filename).exists():
        input_buffer = Path(input_filename).read_text()

        user, created = User.objects.get_or_create(email="jeff.triplett@gmail.com")

        table = Table()

        table.add_column("job-ID")
        table.add_column("prior")
        table.add_column("name")
        table.add_column("user")
        table.add_column("state")
        table.add_column("submit/start")
        table.add_column("at")
        table.add_column("queue")
        table.add_column("slots")
        table.add_column("ja-task-ID")

        rows = parse_output(input_buffer)
        for row in rows:
            """
            TODO: Do something with `state`
            Possible columns:
            - job-ID
            - prior
            - name
            - user
            - state
            - submit/start
            - at
            - queue
            - slots
            - ja-task-ID
            -"""
            table.add_row(
                row["job-ID"],
                row["prior"],
                row["name"],
                row["user"],
                row["state"],
                row["submit/start"],
                row["at"],
                row["queue"],
                row.get("slots"),
                row.get("ja-task-ID"),
            )

            try:
                job_id = row["job-ID"]
                job_state = row["state"]
                job_submitted = f"{row['submit/start']} {row['at']}".replace("/", "-")
                job_submitted = parse(job_submitted)

                if job_submitted:
                    job_submitted = pytz.timezone(settings.TIME_ZONE).localize(
                        job_submitted, is_dst=None
                    )

                job, created = Job.objects.update_or_create(
                    sge_task_id=job_id,
                    defaults={
                        "job_data": row,
                        "job_state": job_state,
                        "job_submitted": job_submitted,
                        "user": user,
                    },
                )
            except Exception as e:
                print(f"{job_id}")
                print(f"{e}")

        console = Console()
        console.print(table)
