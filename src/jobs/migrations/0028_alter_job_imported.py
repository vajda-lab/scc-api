# Generated by Django 3.2.4 on 2021-07-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0027_alter_job_imported"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="imported",
            field=models.BooleanField(
                default=False,
                help_text="Was this job imported from the SCC or created via  OUR API?",
                null=True,
            ),
        ),
    ]
