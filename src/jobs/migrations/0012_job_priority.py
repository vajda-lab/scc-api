# Generated by Django 3.1.7 on 2021-03-19 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0011_auto_20210316_2105"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="priority",
            field=models.BooleanField(default=False),
        ),
    ]
