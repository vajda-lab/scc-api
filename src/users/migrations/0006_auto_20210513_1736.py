# Generated by Django 3.1.9 on 2021-05-13 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_priority"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="affiliation",
        ),
        migrations.RemoveField(
            model_name="user",
            name="max_job_submission",
        ),
        migrations.RemoveField(
            model_name="user",
            name="notes",
        ),
        migrations.RemoveField(
            model_name="user",
            name="organization",
        ),
    ]
