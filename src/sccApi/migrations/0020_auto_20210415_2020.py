# Generated by Django 3.1.7 on 2021-04-15 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sccApi", "0019_auto_20210414_2202"),
    ]

    operations = [
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
                db_index=True,
                default="queued",
                max_length=20,
            ),
        ),
    ]
