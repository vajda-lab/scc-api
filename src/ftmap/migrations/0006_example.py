# Generated by Django 2.1.15 on 2020-03-05 00:23

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ftmap', '0005_job_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('pdb_id', models.CharField(max_length=4)),
                ('pdb_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/static/examples'), upload_to='')),
                ('pse_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/static/examples'), upload_to='')),
            ],
        ),
    ]
