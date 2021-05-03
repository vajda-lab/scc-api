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

    headers = {}
    header_cols = []
    for header_col in range(len(header_keys)):
        header = header_keys[header_col]
        start = lines[0].find(header)
        try:
            next_header = header_keys[header_col + 1]
            end = lines[0].find(next_header)
        except IndexError:
            end = None

        header_cols.append(start)
        headers[header] = {
            "name": header,
            "start": start,
            "end": end,
        }

    rows = []
    for row in lines[2:]:
        data = {}
        for column in headers:
            start = headers[column]["start"]
            end = headers[column]["end"]
            if end:
                data[column] = row[start:end]
            else:
                data[column] = row[start:]
        rows.append(data)
    return rows


@click.command()
@click.argument("input_filename")
def main(input_filename):

    if Path(input_filename).exists():
        input_buffer = Path(input_filename).read_text()
        input_buffer = input_buffer.replace("submit/start at", "submit-start-at")

        user, created = User.objects.get_or_create(email="test@example.com")

        rows = parse_output(input_buffer)

        table = Table()
        table.add_column("job-ID")
        table.add_column("prior")
        table.add_column("name")
        table.add_column("user")
        table.add_column("state")
        table.add_column("submit-start-at")
        table.add_column("queue")
        table.add_column("slots")
        table.add_column("ja-task-ID")

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
                row["submit-start-at"],
                row["queue"],
                row.get("slots"),
                row.get("ja-task-ID"),
            )

            try:
                job_id = row["job-ID"]
                job_ja_task_id = row.get("ja-task-ID")
                job_state = row["state"]
                job_submitted = f"{row['submit-start-at']}".replace("/", "-")
                job_submitted = parse(job_submitted)

                if job_submitted:
                    job_submitted = pytz.timezone(settings.TIME_ZONE).localize(
                        job_submitted, is_dst=None
                    )

                job, created = Job.objects.update_or_create(
                    sge_task_id=job_id,
                    defaults={
                        "job_data": row,
                        "job_ja_task_id": job_ja_task_id,
                        "job_state": job_state,
                        "job_submitted": job_submitted,
                        "user": user,
                    },
                )
            except Exception as e:
                print(f"{job_id} :: {e}")

        console = Console()
        console.print(table)
