# Generated by Django 2.1.9 on 2019-06-05 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "job_status",
                    models.CharField(
                        choices=[("IP", "In Progress"), ("CP", "Complete")],
                        default="IP",
                        max_length=2,
                    ),
                ),
                ("job_name", models.CharField(max_length=40)),
                ("pdb_id", models.CharField(blank=True, max_length=4, null=True)),
            ],
        ),
    ]
