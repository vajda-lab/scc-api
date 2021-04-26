# Generated by Django 3.1.7 on 2021-04-23 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sccApi", "0024_job_job_ja_task_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "active"),
                    ("complete", "complete"),
                    ("deleted", "deleted"),
                    ("error", "error"),
                    ("queued", "queued"),
                ],
                db_index=True,
                default="queued",
                max_length=20,
            ),
        ),
    ]