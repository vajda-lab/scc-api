# Generated by Django 3.1.7 on 2021-04-22 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sccApi", "0022_job_job_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobLog",
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
                ("event", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="sccApi.job"
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "get_latest_by": ["created"],
            },
        ),
    ]
