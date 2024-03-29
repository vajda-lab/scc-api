# Generated by Django 3.1.7 on 2021-03-16 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0010_auto_20200328_0055"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Example",
        ),
        migrations.RemoveField(
            model_name="job",
            name="chain",
        ),
        migrations.RemoveField(
            model_name="job",
            name="pdb_id",
        ),
        migrations.RemoveField(
            model_name="job",
            name="title",
        ),
        migrations.AlterField(
            model_name="job",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "active"),
                    ("complete", "complete"),
                    ("error", "error"),
                    ("deleted", "deleted"),
                    ("queued", "queued"),
                ],
                default="queued",
                max_length=20,
            ),
        ),
    ]
