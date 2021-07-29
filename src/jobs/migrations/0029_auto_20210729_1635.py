# Generated by Django 3.2.5 on 2021-07-29 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0028_alter_job_imported'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='last_exception',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='last_exception_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='last_exception_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
