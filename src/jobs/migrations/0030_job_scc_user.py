# Generated by Django 3.2.5 on 2021-08-26 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0029_auto_20210729_1635"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="scc_user",
            field=models.CharField(blank=True, db_index=True, max_length=20),
        ),
    ]