# Generated by Django 2.1.15 on 2020-03-06 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sccApi", "0007_auto_20200306_1939"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="status",
            field=models.CharField(
                choices=[
                    ("complete", "draft"),
                    ("active", "active"),
                    ("error", "error"),
                    ("deleted", "deleted"),
                ],
                default="active",
                max_length=20,
            ),
        ),
    ]
